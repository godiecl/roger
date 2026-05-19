"""
Georeference — geographic pins for the map view.

Pins come from ACTIVE AttrGeographicReferenceModel records that have lat/lng.
When a record has geographic_location text but no coordinates, the LLM can
infer them via a curator-triggered endpoint.

Validation flow:
  AI-inferred → ACTIVE, source_type=AI  (public, can be reported)
  Curator validates → supersedes AI, inserts ACTIVE with source_type=CURATOR
  User reports via /contributions (geographic field) → PENDING contribution
  Curator can DELETE any active record (even validated ones)
"""

import json
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.features.authenticate.domain.role import Role
from app.features.authenticate.infrastructure.adapters.user_repository import UserRepository
from app.features.authenticate.interfaces.api.dependencies import get_current_user_id
from app.features.taxonomy.infrastructure.persistence.taxonomy_model import (
    AttrGeographicReferenceModel,
    AttributeStatus,
    SourceType,
)
from app.infrastructure.ai.llm.llm_factory import create_llm_provider
from app.infrastructure.database.session import get_db

router = APIRouter(prefix="/georeference", tags=["Georeference"])

_CURATOR_ROLES = (Role.CURADOR, Role.ADMINISTRADOR)


async def _require_curator(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> int:
    user = await UserRepository(db).get_by_id(user_id)
    if not user or user.role not in _CURATOR_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo curadores y administradores.")
    return user_id


# ── Schemas ────────────────────────────────────────────────────────────────────

class PhotoPinResponse(BaseModel):
    photograph_id: int
    attribute_id: int
    title: str
    year: Optional[int]
    location: str
    lat: float
    lng: float
    source: str          # "metadata" | "ai" | "curator"
    validated: bool      # True when source_type == CURATOR
    confidence: Optional[float]


class PinsResponse(BaseModel):
    total: int
    pins: List[PhotoPinResponse]


class InferRequest(BaseModel):
    geographic_location: str
    title: Optional[str] = None
    year: Optional[int] = None


class InferResponse(BaseModel):
    photograph_id: int
    attribute_id: int
    lat: float
    lng: float
    location: str
    source: str


class BatchInferResponse(BaseModel):
    processed: int
    inferred: int
    errors: int


# ── LLM inference helper ───────────────────────────────────────────────────────

_GEO_SYSTEM = """Eres un experto en geografía latinoamericana e historia chilena.
Responde ÚNICAMENTE con JSON válido, sin texto adicional."""

_GEO_PROMPT = """Dada la descripción de una fotografía histórica, infiere las coordenadas
geográficas más probables del lugar donde fue tomada.

Título: {title}
Año aproximado: {year}
Descripción de ubicación: {location}

Responde con este JSON:
{{"lat": <latitud decimal>, "lng": <longitud decimal>, "confidence": <0.0-1.0>}}

Si no puedes inferir coordenadas razonables, responde:
{{"lat": null, "lng": null, "confidence": 0}}"""


async def _infer_coords(location: str, title: str, year: Optional[int]) -> Optional[tuple[float, float, float]]:
    """Call LLM to infer lat/lng from a location description. Returns (lat, lng, confidence) or None."""
    try:
        llm = create_llm_provider()
        raw = await llm.complete([
            {"role": "system", "content": _GEO_SYSTEM},
            {"role": "user", "content": _GEO_PROMPT.format(
                title=title or "Sin título",
                year=str(year) if year else "Desconocido",
                location=location,
            )},
        ])
        raw = raw.strip()
        if raw.startswith("```"):
            lines = raw.split("\n")
            raw = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        data = json.loads(raw)
        lat = data.get("lat")
        lng = data.get("lng")
        conf = float(data.get("confidence", 0.5))
        if lat is None or lng is None:
            return None
        return float(lat), float(lng), conf
    except Exception:
        return None


# ── GET /pins ──────────────────────────────────────────────────────────────────

@router.get("/pins", response_model=PinsResponse)
async def list_pins(
    db: AsyncSession = Depends(get_db),
):
    """
    Returns all active geographic references that have lat/lng coordinates.
    Includes photograph title/year from the view_images table when available.
    """
    from app.features.view_images.infrastructure.persistence.image_model import ImageModel

    result = await db.execute(
        select(AttrGeographicReferenceModel).where(
            AttrGeographicReferenceModel.status == AttributeStatus.ACTIVE,
            AttrGeographicReferenceModel.latitude.is_not(None),
            AttrGeographicReferenceModel.longitude.is_not(None),
        )
    )
    records = result.scalars().all()

    # Build a lookup of photograph metadata from the images view
    photograph_ids = [r.photograph_id for r in records]
    image_lookup: dict[int, ImageModel] = {}
    if photograph_ids:
        img_result = await db.execute(
            select(ImageModel).where(ImageModel.id.in_(photograph_ids))
        )
        for img in img_result.scalars().all():
            image_lookup[img.id] = img

    pins: List[PhotoPinResponse] = []
    for rec in records:
        img = image_lookup.get(rec.photograph_id)
        source = rec.source_type.value if rec.source_type else "ai"
        # Normalize source label for frontend
        if source == "curator":
            source_label = "curator"
        elif source == "ai":
            source_label = "ai"
        else:
            source_label = "metadata"

        pins.append(PhotoPinResponse(
            photograph_id=rec.photograph_id,
            attribute_id=rec.id,
            title=img.title if img else f"Fotografía #{rec.photograph_id}",
            year=img.year if img else None,
            location=rec.geographic_location or "",
            lat=rec.latitude,
            lng=rec.longitude,
            source=source_label,
            validated=rec.source_type == SourceType.CURATOR,
            confidence=rec.confidence_level,
        ))

    return PinsResponse(total=len(pins), pins=pins)


# ── POST /infer/{photograph_id} ────────────────────────────────────────────────

@router.post("/infer/{photograph_id}", response_model=InferResponse, status_code=status.HTTP_201_CREATED)
async def infer_coordinates(
    photograph_id: int,
    request: InferRequest,
    user_id: int = Depends(_require_curator),
    db: AsyncSession = Depends(get_db),
):
    """
    Calls the LLM to infer lat/lng for a photograph that has a location description
    but no coordinates. Creates an ACTIVE record with source_type=AI.
    Supersedes any previous ACTIVE record for this photograph.
    """
    coords = await _infer_coords(request.geographic_location, request.title or "", request.year)
    if not coords:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No fue posible inferir coordenadas para esta ubicación.",
        )
    lat, lng, confidence = coords

    # Supersede existing ACTIVE records
    existing_result = await db.execute(
        select(AttrGeographicReferenceModel).where(
            AttrGeographicReferenceModel.photograph_id == photograph_id,
            AttrGeographicReferenceModel.status == AttributeStatus.ACTIVE,
        )
    )
    for old in existing_result.scalars().all():
        old.status = AttributeStatus.SUPERSEDED

    llm = create_llm_provider()
    new_rec = AttrGeographicReferenceModel(
        photograph_id=photograph_id,
        status=AttributeStatus.ACTIVE,
        source_type=SourceType.AI,
        geographic_location=request.geographic_location,
        latitude=lat,
        longitude=lng,
        confidence_level=confidence,
        analysis_provider=llm.provider_name,
    )
    db.add(new_rec)
    await db.flush()
    await db.refresh(new_rec)

    return InferResponse(
        photograph_id=photograph_id,
        attribute_id=new_rec.id,
        lat=lat,
        lng=lng,
        location=request.geographic_location,
        source="ai",
    )


# ── POST /batch-infer ──────────────────────────────────────────────────────────

@router.post("/batch-infer", response_model=BatchInferResponse)
async def batch_infer(
    user_id: int = Depends(_require_curator),
    db: AsyncSession = Depends(get_db),
):
    """
    For all ACTIVE geographic references that have a geographic_location but
    no lat/lng, calls the LLM and saves the inferred coordinates.
    """
    from app.features.view_images.infrastructure.persistence.image_model import ImageModel

    result = await db.execute(
        select(AttrGeographicReferenceModel).where(
            AttrGeographicReferenceModel.status == AttributeStatus.ACTIVE,
            AttrGeographicReferenceModel.latitude.is_(None),
            AttrGeographicReferenceModel.geographic_location.is_not(None),
        )
    )
    candidates = result.scalars().all()

    photograph_ids = [r.photograph_id for r in candidates]
    image_lookup: dict[int, ImageModel] = {}
    if photograph_ids:
        img_res = await db.execute(select(ImageModel).where(ImageModel.id.in_(photograph_ids)))
        for img in img_res.scalars().all():
            image_lookup[img.id] = img

    processed = inferred = errors = 0
    llm = create_llm_provider()

    for rec in candidates:
        processed += 1
        img = image_lookup.get(rec.photograph_id)
        coords = await _infer_coords(
            rec.geographic_location,
            img.title if img else "",
            img.year if img else None,
        )
        if not coords:
            errors += 1
            continue
        lat, lng, confidence = coords
        rec.latitude = lat
        rec.longitude = lng
        rec.confidence_level = confidence
        rec.source_type = SourceType.AI
        rec.analysis_provider = llm.provider_name
        inferred += 1

    return BatchInferResponse(processed=processed, inferred=inferred, errors=errors)


# ── POST /validate/{photograph_id} ────────────────────────────────────────────

@router.post("/validate/{photograph_id}", status_code=status.HTTP_200_OK)
async def validate_georeference(
    photograph_id: int,
    user_id: int = Depends(_require_curator),
    db: AsyncSession = Depends(get_db),
):
    """
    Curator validates/confirms the active georeference for a photograph.
    Supersedes the current ACTIVE record and creates a new one with
    source_type=CURATOR. Once validated, public users cannot propose removal.
    Curators can still delete it via DELETE /georeference/{attribute_id}.
    """
    result = await db.execute(
        select(AttrGeographicReferenceModel).where(
            AttrGeographicReferenceModel.photograph_id == photograph_id,
            AttrGeographicReferenceModel.status == AttributeStatus.ACTIVE,
        )
    )
    active = result.scalars().first()
    if not active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hay referencia geográfica activa para esta fotografía.")
    if active.latitude is None or active.longitude is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="La referencia activa no tiene coordenadas para validar.")

    # Supersede existing
    result_all = await db.execute(
        select(AttrGeographicReferenceModel).where(
            AttrGeographicReferenceModel.photograph_id == photograph_id,
            AttrGeographicReferenceModel.status == AttributeStatus.ACTIVE,
        )
    )
    for old in result_all.scalars().all():
        old.status = AttributeStatus.SUPERSEDED

    validated = AttrGeographicReferenceModel(
        photograph_id=photograph_id,
        status=AttributeStatus.ACTIVE,
        source_type=SourceType.CURATOR,
        geographic_location=active.geographic_location,
        latitude=active.latitude,
        longitude=active.longitude,
        location_type=active.location_type,
        location_radius_km=active.location_radius_km,
        signage_found=active.signage_found,
        architectural_landmarks=active.architectural_landmarks,
        landscape_features=active.landscape_features,
        confidence_level=active.confidence_level,
        analysis_provider=f"curator:{user_id}",
    )
    db.add(validated)
    await db.flush()
    await db.refresh(validated)

    return {
        "photograph_id": photograph_id,
        "attribute_id": validated.id,
        "source": "curator",
        "validated": True,
    }


# ── DELETE /{attribute_id} ────────────────────────────────────────────────────

@router.delete("/{attribute_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_georeference(
    attribute_id: int,
    user_id: int = Depends(_require_curator),
    db: AsyncSession = Depends(get_db),
):
    """
    Curator supersedes (soft-deletes) a geographic reference record.
    Works on any record regardless of source_type — including validated ones.
    """
    result = await db.execute(
        select(AttrGeographicReferenceModel).where(
            AttrGeographicReferenceModel.id == attribute_id,
        )
    )
    rec = result.scalar_one_or_none()
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Referencia geográfica no encontrada.")
    if rec.status == AttributeStatus.SUPERSEDED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Este registro ya fue superseded.")

    rec.status = AttributeStatus.SUPERSEDED
    return None
