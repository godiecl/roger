"""
FastAPI routes for the taxonomy feature.
Attribute 01 (Technical Metadata): extract and query.
Write/analysis requires CURADOR or ADMINISTRADOR role.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.authenticate.domain.role import Role
from app.features.authenticate.infrastructure.adapters.user_repository import UserRepository
from app.features.authenticate.interfaces.api.dependencies import get_current_user_id
from app.features.taxonomy.application.extract_technical_metadata_usecase import (
    ExtractTechnicalMetadataUseCase,
)
from app.features.taxonomy.application.get_technical_metadata_usecase import (
    GetTechnicalMetadataUseCase,
)
from app.features.taxonomy.infrastructure.adapters.taxonomy_repository import TaxonomyRepository
from app.features.taxonomy.interfaces.api.schemas import (
    AnalyzeResponse,
    TechnicalMetadataHistoryResponse,
    TechnicalMetadataResponse,
    ChronologyWriteRequest, ChronologyResponse,
    GeographicWriteRequest, GeographicResponse,
    EnvironmentalWriteRequest, EnvironmentalResponse,
)
from app.features.taxonomy.infrastructure.persistence.taxonomy_model import (
    AttrChronologyDatingModel, AttrGeographicReferenceModel, AttrEnvironmentalSpatialModel,
    AttributeStatus, SourceType,
)
from sqlalchemy import update as sa_update
from app.infrastructure.database.session import get_db
from app.shared.domain.exceptions import EntityNotFoundError


router = APIRouter(prefix="/taxonomy", tags=["Taxonomy"])


async def _require_write_access(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> int:
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if not user or user.role not in (Role.CURADOR, Role.ADMINISTRADOR):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo curadores y administradores pueden ejecutar análisis.",
        )
    return user_id


# ── Attribute 01 — Technical Metadata ─────────────────────────────────────────

@router.post(
    "/photographs/{photograph_id}/technical/analyze",
    response_model=AnalyzeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Extraer metadatos técnicos (Atributo 01)",
    description=(
        "Analiza el archivo master (o mejor disponible) de la fotografía con Pillow/ExifTool. "
        "Si ya existía un registro ACTIVE, lo marca como SUPERSEDED y crea uno nuevo. "
        "Registra un AnalysisJob para trazabilidad."
    ),
)
async def analyze_technical(
    photograph_id: int,
    user_id: int = Depends(_require_write_access),
    db: AsyncSession = Depends(get_db),
):
    try:
        repo = TaxonomyRepository(db)
        usecase = ExtractTechnicalMetadataUseCase(repo, db)
        record = await usecase.execute(photograph_id=photograph_id, triggered_by=user_id)
        return AnalyzeResponse(
            message="Metadatos técnicos extraídos correctamente.",
            photograph_id=photograph_id,
            record=TechnicalMetadataResponse(**record.__dict__),
        )
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.get(
    "/photographs/{photograph_id}/technical",
    response_model=TechnicalMetadataResponse,
    summary="Obtener metadatos técnicos activos (Atributo 01)",
)
async def get_technical(
    photograph_id: int,
    _: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    try:
        repo = TaxonomyRepository(db)
        usecase = GetTechnicalMetadataUseCase(repo)
        record = await usecase.execute_active(photograph_id)
        return TechnicalMetadataResponse(**record.__dict__)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/photographs/{photograph_id}/technical/history",
    response_model=TechnicalMetadataHistoryResponse,
    summary="Historial completo de metadatos técnicos (Atributo 01)",
)
async def get_technical_history(
    photograph_id: int,
    _: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = TaxonomyRepository(db)
    usecase = GetTechnicalMetadataUseCase(repo)
    records = await usecase.execute_history(photograph_id)
    return TechnicalMetadataHistoryResponse(
        photograph_id=photograph_id,
        total=len(records),
        records=[TechnicalMetadataResponse(**r.__dict__) for r in records],
    )


# ── Curator direct write helpers ───────────────────────────────────────────────

async def _supersede_active(session, model_cls, photograph_id: int) -> None:
    await session.execute(
        sa_update(model_cls)
        .where(model_cls.photograph_id == photograph_id, model_cls.status == AttributeStatus.ACTIVE)
        .values(status=AttributeStatus.SUPERSEDED)
    )


def _to_dict(model) -> dict:
    from sqlalchemy.inspection import inspect
    return {c.key: getattr(model, c.key) for c in inspect(model).mapper.column_attrs}


# ── Attribute 02 — Chronology & Dating ────────────────────────────────────────

@router.put(
    "/photographs/{photograph_id}/chronology",
    response_model=ChronologyResponse,
    status_code=status.HTTP_200_OK,
    summary="Escritura directa curador — Atributo 02 (Cronología)",
)
async def write_chronology(
    photograph_id: int,
    request: ChronologyWriteRequest,
    _: int = Depends(_require_write_access),
    db: AsyncSession = Depends(get_db),
):
    await _supersede_active(db, AttrChronologyDatingModel, photograph_id)
    model = AttrChronologyDatingModel(
        photograph_id=photograph_id,
        status=AttributeStatus.ACTIVE,
        source_type=SourceType.CURATOR,
        date_type=request.date_type,
        precise_date=request.precise_date,
        date_from=request.date_from,
        date_to=request.date_to,
        date_hypothesis=request.date_hypothesis,
        verification_source=request.verification_source,
        methodology=request.methodology,
        visual_evidence_notes=request.visual_evidence_notes,
    )
    db.add(model)
    await db.flush()
    await db.refresh(model)
    return ChronologyResponse(**_to_dict(model))


@router.get(
    "/photographs/{photograph_id}/chronology",
    response_model=ChronologyResponse,
    summary="Obtener cronología activa (Atributo 02)",
)
async def get_chronology(
    photograph_id: int,
    _: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy.future import select
    result = await db.execute(
        select(AttrChronologyDatingModel)
        .where(AttrChronologyDatingModel.photograph_id == photograph_id,
               AttrChronologyDatingModel.status == AttributeStatus.ACTIVE)
        .order_by(AttrChronologyDatingModel.id.desc()).limit(1)
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Sin cronología activa para esta fotografía.")
    return ChronologyResponse(**_to_dict(model))


# ── Attribute 03 — Geographic Reference ───────────────────────────────────────

@router.put(
    "/photographs/{photograph_id}/geographic",
    response_model=GeographicResponse,
    status_code=status.HTTP_200_OK,
    summary="Escritura directa curador — Atributo 03 (Referencia Geográfica)",
)
async def write_geographic(
    photograph_id: int,
    request: GeographicWriteRequest,
    _: int = Depends(_require_write_access),
    db: AsyncSession = Depends(get_db),
):
    await _supersede_active(db, AttrGeographicReferenceModel, photograph_id)
    model = AttrGeographicReferenceModel(
        photograph_id=photograph_id,
        status=AttributeStatus.ACTIVE,
        source_type=SourceType.CURATOR,
        location_type=request.location_type,
        geographic_location=request.geographic_location,
        latitude=request.latitude,
        longitude=request.longitude,
        location_radius_km=request.location_radius_km,
        signage_found=request.signage_found,
        architectural_landmarks=request.architectural_landmarks,
        landscape_features=request.landscape_features,
    )
    db.add(model)
    await db.flush()
    await db.refresh(model)
    return GeographicResponse(**_to_dict(model))


@router.get(
    "/photographs/{photograph_id}/geographic",
    response_model=GeographicResponse,
    summary="Obtener referencia geográfica activa (Atributo 03)",
)
async def get_geographic(
    photograph_id: int,
    _: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy.future import select
    result = await db.execute(
        select(AttrGeographicReferenceModel)
        .where(AttrGeographicReferenceModel.photograph_id == photograph_id,
               AttrGeographicReferenceModel.status == AttributeStatus.ACTIVE)
        .order_by(AttrGeographicReferenceModel.id.desc()).limit(1)
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Sin referencia geográfica activa para esta fotografía.")
    return GeographicResponse(**_to_dict(model))


# ── Attribute 04 — Environmental & Spatial ────────────────────────────────────

@router.put(
    "/photographs/{photograph_id}/environmental",
    response_model=EnvironmentalResponse,
    status_code=status.HTTP_200_OK,
    summary="Escritura directa curador — Atributo 04 (Contexto Ambiental/Espacial)",
)
async def write_environmental(
    photograph_id: int,
    request: EnvironmentalWriteRequest,
    _: int = Depends(_require_write_access),
    db: AsyncSession = Depends(get_db),
):
    await _supersede_active(db, AttrEnvironmentalSpatialModel, photograph_id)
    model = AttrEnvironmentalSpatialModel(
        photograph_id=photograph_id,
        status=AttributeStatus.ACTIVE,
        source_type=SourceType.CURATOR,
        setting_type=request.setting_type,
        specific_typology=request.specific_typology,
        conservation_state=request.conservation_state,
        human_env_relationship=request.human_env_relationship,
    )
    db.add(model)
    await db.flush()
    await db.refresh(model)
    return EnvironmentalResponse(**_to_dict(model))


@router.get(
    "/photographs/{photograph_id}/environmental",
    response_model=EnvironmentalResponse,
    summary="Obtener contexto ambiental activo (Atributo 04)",
)
async def get_environmental(
    photograph_id: int,
    _: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy.future import select
    result = await db.execute(
        select(AttrEnvironmentalSpatialModel)
        .where(AttrEnvironmentalSpatialModel.photograph_id == photograph_id,
               AttrEnvironmentalSpatialModel.status == AttributeStatus.ACTIVE)
        .order_by(AttrEnvironmentalSpatialModel.id.desc()).limit(1)
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Sin contexto ambiental activo para esta fotografía.")
    return EnvironmentalResponse(**_to_dict(model))
