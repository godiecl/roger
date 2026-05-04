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
)
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
