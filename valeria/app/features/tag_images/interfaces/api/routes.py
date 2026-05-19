"""
tag_images — Etiquetado IA + aprobación por curador.

El LLM sugiere tags basados en metadatos de la fotografía.
Se almacenan como PENDING con source=AI hasta aprobación del curador.
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
from app.features.tagging.infrastructure.persistence.tag_model import (
    TagCategory, TagModel, TagSource, TagStatus, PhotographTagModel,
)
from app.infrastructure.ai.llm.llm_factory import create_llm_provider
from app.infrastructure.database.session import get_db

router = APIRouter(prefix="/tag-images", tags=["Tag Images (AI)"])

_WRITE_ROLES = (Role.CURADOR, Role.ADMINISTRADOR)


async def _require_write(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> int:
    user = await UserRepository(db).get_by_id(user_id)
    if not user or user.role not in _WRITE_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo curadores y administradores.")
    return user_id


# ── Schemas ────────────────────────────────────────────────────────────────────

class GenerateTagsRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    year: Optional[int] = None
    location: Optional[str] = None
    detected_objects: Optional[List[str]] = None


class PendingTagResponse(BaseModel):
    photograph_tag_id: int
    photograph_id: int
    tag_id: int
    tag_name: str
    tag_category: str
    confidence: Optional[float]
    created_at: datetime

    model_config = {"from_attributes": True}


class GenerateTagsResponse(BaseModel):
    photograph_id: int
    generated: int
    tags: List[PendingTagResponse]


class PendingTagsListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    items: List[PendingTagResponse]


_SYSTEM_PROMPT = """Eres un catalogador experto en fotografía patrimonial histórica latinoamericana.
Tu tarea es sugerir etiquetas descriptivas precisas para una fotografía de la colección Gerstmann.

Responde ÚNICAMENTE con JSON válido, sin texto adicional."""

_USER_PROMPT_TEMPLATE = """Sugiere entre 5 y 8 etiquetas descriptivas para esta fotografía:

Título: {title}
Descripción: {description}
Año aproximado: {year}
Ubicación: {location}
Objetos detectados: {objects}

Cada etiqueta debe pertenecer a una de estas categorías:
- geographic: lugares, regiones, países
- temporal: décadas, períodos históricos, épocas
- iconographic: personas, objetos, escenas, actividades
- technical: características técnicas de la fotografía
- ai_inferred: inferencias o interpretaciones basadas en el contenido visual

Responde con este JSON exacto:
{{
  "tags": [
    {{"name": "nombre_etiqueta", "category": "geographic|temporal|iconographic|technical|ai_inferred", "confidence": 0.0-1.0}}
  ]
}}

Las etiquetas deben ser en español, en minúsculas y sin caracteres especiales."""


async def _get_or_create_tag(db: AsyncSession, name: str, category: TagCategory) -> TagModel:
    result = await db.execute(
        select(TagModel).where(TagModel.name == name, TagModel.collection_id.is_(None))
    )
    tag = result.scalar_one_or_none()
    if not tag:
        tag = TagModel(name=name, category=category, collection_id=None)
        db.add(tag)
        await db.flush()
        await db.refresh(tag)
    return tag


# ── Generate ───────────────────────────────────────────────────────────────────

@router.post("/generate/{photograph_id}", response_model=GenerateTagsResponse, status_code=status.HTTP_201_CREATED)
async def generate_tags(
    photograph_id: int,
    request: GenerateTagsRequest,
    user_id: int = Depends(_require_write),
    db: AsyncSession = Depends(get_db),
):
    """
    El LLM sugiere tags para la fotografía.
    Se crean en el vocabulario controlado (si no existen) y se asignan
    como PENDING con source=AI para revisión del curador.
    """
    llm = create_llm_provider()

    prompt = _USER_PROMPT_TEMPLATE.format(
        title=request.title or "Sin título",
        description=request.description or "Sin descripción",
        year=str(request.year) if request.year else "Desconocido",
        location=request.location or "Desconocida",
        objects=", ".join(request.detected_objects) if request.detected_objects else "No detectados",
    )

    try:
        raw = await llm.complete([
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ])
        raw = raw.strip()
        if raw.startswith("```"):
            lines = raw.split("\n")
            raw = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        data = json.loads(raw)
        suggestions = data.get("tags", [])
    except Exception:
        suggestions = []

    created: List[PendingTagResponse] = []

    for suggestion in suggestions[:8]:
        name = str(suggestion.get("name", "")).strip().lower()[:255]
        if not name:
            continue

        try:
            category = TagCategory(suggestion.get("category", "ai_inferred"))
        except ValueError:
            category = TagCategory.AI_INFERRED

        confidence = suggestion.get("confidence")
        if confidence is not None:
            try:
                confidence = max(0.0, min(1.0, float(confidence)))
            except (TypeError, ValueError):
                confidence = None

        tag = await _get_or_create_tag(db, name, category)

        existing = await db.execute(
            select(PhotographTagModel).where(
                PhotographTagModel.photograph_id == photograph_id,
                PhotographTagModel.tag_id == tag.id,
                PhotographTagModel.source == TagSource.AI,
            )
        )
        if existing.scalar_one_or_none():
            continue

        pt = PhotographTagModel(
            photograph_id=photograph_id,
            tag_id=tag.id,
            source=TagSource.AI,
            confidence=confidence,
            status=TagStatus.PENDING,
        )
        db.add(pt)
        await db.flush()
        await db.refresh(pt)

        created.append(PendingTagResponse(
            photograph_tag_id=pt.id,
            photograph_id=pt.photograph_id,
            tag_id=pt.tag_id,
            tag_name=tag.name,
            tag_category=tag.category.value,
            confidence=pt.confidence,
            created_at=pt.created_at,
        ))

    return GenerateTagsResponse(
        photograph_id=photograph_id,
        generated=len(created),
        tags=created,
    )


# ── Pending list ───────────────────────────────────────────────────────────────

@router.get("/pending", response_model=PendingTagsListResponse)
async def list_pending_tags(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    photograph_id: Optional[int] = Query(None),
    _: int = Depends(_require_write),
    db: AsyncSession = Depends(get_db),
):
    """Lista tags AI pendientes de aprobación."""
    from sqlalchemy import func

    q = (
        select(PhotographTagModel, TagModel)
        .join(TagModel, PhotographTagModel.tag_id == TagModel.id)
        .where(PhotographTagModel.source == TagSource.AI, PhotographTagModel.status == TagStatus.PENDING)
    )
    if photograph_id:
        q = q.where(PhotographTagModel.photograph_id == photograph_id)
    q = q.order_by(PhotographTagModel.created_at.asc())

    count_q = select(func.count(PhotographTagModel.id)).where(
        PhotographTagModel.source == TagSource.AI,
        PhotographTagModel.status == TagStatus.PENDING,
    )
    if photograph_id:
        count_q = count_q.where(PhotographTagModel.photograph_id == photograph_id)

    total_result = await db.execute(count_q)
    total = total_result.scalar_one()

    result = await db.execute(q.offset(skip).limit(limit))
    rows = result.all()

    return PendingTagsListResponse(
        total=total,
        skip=skip,
        limit=limit,
        items=[
            PendingTagResponse(
                photograph_tag_id=pt.id,
                photograph_id=pt.photograph_id,
                tag_id=pt.tag_id,
                tag_name=tag.name,
                tag_category=tag.category.value,
                confidence=pt.confidence,
                created_at=pt.created_at,
            )
            for pt, tag in rows
        ],
    )


# ── Approve / Reject ───────────────────────────────────────────────────────────

@router.post("/{photograph_tag_id}/approve", status_code=status.HTTP_200_OK)
async def approve_tag(
    photograph_tag_id: int,
    user_id: int = Depends(_require_write),
    db: AsyncSession = Depends(get_db),
):
    """Aprueba un tag AI — pasa a APPROVED."""
    result = await db.execute(
        select(PhotographTagModel).where(PhotographTagModel.id == photograph_tag_id)
    )
    pt = result.scalar_one_or_none()
    if not pt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag no encontrado.")
    if pt.source != TagSource.AI:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Solo se pueden aprobar tags de origen AI.")

    pt.status = TagStatus.APPROVED
    pt.approved_by = user_id
    pt.approved_at = datetime.now(timezone.utc)
    await db.flush()

    return {"id": pt.id, "status": pt.status.value}


@router.delete("/{photograph_tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def reject_tag(
    photograph_tag_id: int,
    _: int = Depends(_require_write),
    db: AsyncSession = Depends(get_db),
):
    """Rechaza (elimina) un tag AI pendiente."""
    result = await db.execute(
        select(PhotographTagModel).where(PhotographTagModel.id == photograph_tag_id)
    )
    pt = result.scalar_one_or_none()
    if not pt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag no encontrado.")
    if pt.source != TagSource.AI or pt.status != TagStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Solo se pueden eliminar tags AI pendientes.")

    await db.delete(pt)
    return None


# ── Tags for a photograph (public) ────────────────────────────────────────────

class ApprovedTagResponse(BaseModel):
    photograph_tag_id: int
    photograph_id: int
    tag_id: int
    tag_name: str
    tag_category: str
    source: str
    confidence: Optional[float]
    created_at: datetime

    model_config = {"from_attributes": True}


class ApprovedTagsListResponse(BaseModel):
    photograph_id: int
    total: int
    tags: List[ApprovedTagResponse]


@router.get("/photograph/{photograph_id}", response_model=ApprovedTagsListResponse)
async def list_photograph_tags(
    photograph_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Returns all APPROVED tags for a photograph, with source info (ai/metadata/manual)."""
    from sqlalchemy import func

    result = await db.execute(
        select(PhotographTagModel, TagModel)
        .join(TagModel, PhotographTagModel.tag_id == TagModel.id)
        .where(
            PhotographTagModel.photograph_id == photograph_id,
            PhotographTagModel.status == TagStatus.APPROVED,
        )
        .order_by(PhotographTagModel.source.asc(), TagModel.name.asc())
    )
    rows = result.all()

    count_result = await db.execute(
        select(func.count(PhotographTagModel.id)).where(
            PhotographTagModel.photograph_id == photograph_id,
            PhotographTagModel.status == TagStatus.APPROVED,
        )
    )
    total = count_result.scalar_one()

    return ApprovedTagsListResponse(
        photograph_id=photograph_id,
        total=total,
        tags=[
            ApprovedTagResponse(
                photograph_tag_id=pt.id,
                photograph_id=pt.photograph_id,
                tag_id=pt.tag_id,
                tag_name=tag.name,
                tag_category=tag.category.value,
                source=pt.source.value,
                confidence=pt.confidence,
                created_at=pt.created_at,
            )
            for pt, tag in rows
        ],
    )


# ── Extract metadata tags ──────────────────────────────────────────────────────

class MetadataTagsResponse(BaseModel):
    photograph_id: int
    extracted: int
    tags: List[PendingTagResponse]


@router.post("/extract-metadata-tags/{photograph_id}", response_model=MetadataTagsResponse, status_code=status.HTTP_200_OK)
async def extract_metadata_tags(
    photograph_id: int,
    user_id: int = Depends(_require_write),
    db: AsyncSession = Depends(get_db),
):
    """
    Extracts tags from active taxonomy attributes (geographic, chronological,
    environmental) and creates APPROVED tags with source=METADATA.
    Idempotent — skips tags that already exist with source=METADATA.
    """
    from app.features.taxonomy.infrastructure.persistence.taxonomy_model import (
        AttrGeographicReferenceModel,
        AttrChronologyDatingModel,
        AttrEnvironmentalSpatialModel,
        AttributeStatus,
    )

    created: List[PendingTagResponse] = []

    async def _upsert(name: str, category: TagCategory) -> None:
        name = name.strip().lower()[:255]
        if not name:
            return
        tag = await _get_or_create_tag(db, name, category)
        existing = await db.execute(
            select(PhotographTagModel).where(
                PhotographTagModel.photograph_id == photograph_id,
                PhotographTagModel.tag_id == tag.id,
                PhotographTagModel.source == TagSource.METADATA,
            )
        )
        if existing.scalar_one_or_none():
            return
        pt = PhotographTagModel(
            photograph_id=photograph_id,
            tag_id=tag.id,
            source=TagSource.METADATA,
            confidence=1.0,
            status=TagStatus.APPROVED,
            approved_by=user_id,
            approved_at=datetime.now(timezone.utc),
        )
        db.add(pt)
        await db.flush()
        await db.refresh(pt)
        created.append(PendingTagResponse(
            photograph_tag_id=pt.id,
            photograph_id=pt.photograph_id,
            tag_id=pt.tag_id,
            tag_name=tag.name,
            tag_category=tag.category.value,
            confidence=pt.confidence,
            created_at=pt.created_at,
        ))

    # Geographic
    geo_res = await db.execute(
        select(AttrGeographicReferenceModel).where(
            AttrGeographicReferenceModel.photograph_id == photograph_id,
            AttrGeographicReferenceModel.status == AttributeStatus.ACTIVE,
        )
    )
    geo = geo_res.scalars().first()
    if geo and geo.geographic_location:
        await _upsert(geo.geographic_location, TagCategory.GEOGRAPHIC)

    # Chronological
    chron_res = await db.execute(
        select(AttrChronologyDatingModel).where(
            AttrChronologyDatingModel.photograph_id == photograph_id,
            AttrChronologyDatingModel.status == AttributeStatus.ACTIVE,
        )
    )
    chron = chron_res.scalars().first()
    if chron:
        year_str = None
        if chron.precise_date:
            year_str = str(chron.precise_date.year)
        elif chron.date_from:
            year_str = f"{chron.date_from.year}s"
        if year_str:
            await _upsert(year_str, TagCategory.TEMPORAL)

    # Environmental
    env_res = await db.execute(
        select(AttrEnvironmentalSpatialModel).where(
            AttrEnvironmentalSpatialModel.photograph_id == photograph_id,
            AttrEnvironmentalSpatialModel.status == AttributeStatus.ACTIVE,
        )
    )
    env = env_res.scalars().first()
    if env:
        if env.setting_type:
            await _upsert(env.setting_type.value, TagCategory.ICONOGRAPHIC)
        if env.specific_typology:
            await _upsert(env.specific_typology, TagCategory.ICONOGRAPHIC)

    return MetadataTagsResponse(
        photograph_id=photograph_id,
        extracted=len(created),
        tags=created,
    )
