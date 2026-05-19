"""
manage_metadata — Auditoría y vista completa de metadatos por fotografía.

Agrega en un solo endpoint el estado de todos los atributos (01-04),
el historial de versiones (ACTIVE/SUPERSEDED/PENDING) y las contribuciones
pendientes para que el curador tenga una vista unificada.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.features.authenticate.domain.role import Role
from app.features.authenticate.infrastructure.adapters.user_repository import UserRepository
from app.features.authenticate.interfaces.api.dependencies import get_current_user_id
from app.features.contributions.domain.contribution import ContributionStatus
from app.features.contributions.infrastructure.adapters.contribution_repository import ContributionRepository
from app.features.taxonomy.infrastructure.persistence.taxonomy_model import (
    AttrTechnicalMetadataModel,
    AttrChronologyDatingModel,
    AttrGeographicReferenceModel,
    AttrEnvironmentalSpatialModel,
    AttributeStatus,
)
from app.infrastructure.database.session import get_db

router = APIRouter(prefix="/metadata", tags=["Metadata Audit"])

_REVIEWER_ROLES = (Role.CURADOR, Role.MESA_EVALUADORA, Role.ADMINISTRADOR)


async def _require_reviewer(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> int:
    user = await UserRepository(db).get_by_id(user_id)
    if not user or user.role not in _REVIEWER_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso restringido a curadores.")
    return user_id


# ── Schemas ────────────────────────────────────────────────────────────────────

class AttributeRecordResponse(BaseModel):
    id: int
    status: str
    source_type: Optional[str] = None
    analyzed_at: Optional[datetime] = None
    confidence_level: Optional[float] = None
    analysis_provider: Optional[str] = None
    data: Dict[str, Any]


class ContributionSummary(BaseModel):
    id: int
    attribute_type: str
    field_name: str
    proposed_value: str
    evidence_notes: Optional[str]
    contributor_id: int
    created_at: Optional[datetime]


class PhotographMetadataResponse(BaseModel):
    photograph_id: int
    technical: List[AttributeRecordResponse]
    chronology: List[AttributeRecordResponse]
    geographic: List[AttributeRecordResponse]
    environmental: List[AttributeRecordResponse]
    pending_contributions: List[ContributionSummary]
    pending_count: int


def _model_to_record(model, exclude: set = None) -> AttributeRecordResponse:
    exclude = exclude or {"id", "photograph_id", "status", "source_type", "analyzed_at",
                          "confidence_level", "analysis_provider", "raw_output"}
    from sqlalchemy.inspection import inspect as sa_inspect
    cols = {c.key: getattr(model, c.key) for c in sa_inspect(model).mapper.column_attrs}
    data = {k: v for k, v in cols.items() if k not in exclude and v is not None}
    return AttributeRecordResponse(
        id=model.id,
        status=model.status.value if hasattr(model.status, "value") else str(model.status),
        source_type=model.source_type.value if hasattr(model, "source_type") and model.source_type else None,
        analyzed_at=model.analyzed_at,
        confidence_level=getattr(model, "confidence_level", None),
        analysis_provider=getattr(model, "analysis_provider", None),
        data=data,
    )


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.get("/{photograph_id}", response_model=PhotographMetadataResponse)
async def get_photograph_metadata(
    photograph_id: int,
    include_superseded: bool = Query(False),
    _: int = Depends(_require_reviewer),
    db: AsyncSession = Depends(get_db),
):
    """
    Vista completa de metadatos de una fotografía para el curador.

    Devuelve todos los registros de los 4 atributos de taxonomía
    (opcionalmente incluyendo los SUPERSEDED) y las contribuciones PENDING.
    """
    statuses = [AttributeStatus.ACTIVE, AttributeStatus.PENDING]
    if include_superseded:
        statuses.append(AttributeStatus.SUPERSEDED)

    async def _fetch(model_cls):
        result = await db.execute(
            select(model_cls)
            .where(model_cls.photograph_id == photograph_id,
                   model_cls.status.in_(statuses))
            .order_by(model_cls.id.desc())
        )
        return result.scalars().all()

    technical = await _fetch(AttrTechnicalMetadataModel)
    chronology = await _fetch(AttrChronologyDatingModel)
    geographic = await _fetch(AttrGeographicReferenceModel)
    environmental = await _fetch(AttrEnvironmentalSpatialModel)

    repo = ContributionRepository(db)
    pending = await repo.list_by_photograph(photograph_id, status=ContributionStatus.PENDING)

    return PhotographMetadataResponse(
        photograph_id=photograph_id,
        technical=[_model_to_record(m) for m in technical],
        chronology=[_model_to_record(m) for m in chronology],
        geographic=[_model_to_record(m) for m in geographic],
        environmental=[_model_to_record(m) for m in environmental],
        pending_contributions=[
            ContributionSummary(
                id=c.id,
                attribute_type=c.attribute_type.value,
                field_name=c.field_name,
                proposed_value=c.proposed_value,
                evidence_notes=c.evidence_notes,
                contributor_id=c.contributor_id,
                created_at=c.created_at,
            )
            for c in pending
        ],
        pending_count=len(pending),
    )


@router.get("", response_model=List[Dict[str, Any]])
async def list_photographs_with_pending(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    _: int = Depends(_require_reviewer),
    db: AsyncSession = Depends(get_db),
):
    """
    Lista fotografías que tienen metadatos PENDING — cola de trabajo del curador.
    """
    from app.features.contributions.infrastructure.persistence.contribution_model import MetadataContributionModel
    from sqlalchemy import distinct

    result = await db.execute(
        select(distinct(MetadataContributionModel.photograph_id))
        .where(MetadataContributionModel.status == ContributionStatus.PENDING)
        .offset(skip)
        .limit(limit)
    )
    photo_ids = result.scalars().all()

    items = []
    for pid in photo_ids:
        repo = ContributionRepository(db)
        pending = await repo.list_by_photograph(pid, status=ContributionStatus.PENDING)
        items.append({"photograph_id": pid, "pending_contributions": len(pending)})

    return items
