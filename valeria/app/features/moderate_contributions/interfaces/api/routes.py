"""
moderate_contributions — Panel de moderación para curadores y evaluadores.

Agrega estadísticas, cola unificada y operaciones batch sobre contribuciones pendientes.
Las operaciones atómicas (approve/reject individual) se delegan al slice contributions.
"""

from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.features.authenticate.domain.role import Role
from app.features.authenticate.infrastructure.adapters.user_repository import UserRepository
from app.features.authenticate.interfaces.api.dependencies import get_current_user_id
from app.features.contributions.application.approve_contribution_usecase import ApproveContributionUseCase
from app.features.contributions.application.reject_contribution_usecase import RejectContributionUseCase
from app.features.contributions.domain.contribution import ContributionAttributeType, ContributionStatus
from app.features.contributions.infrastructure.adapters.contribution_repository import ContributionRepository
from app.features.contributions.infrastructure.persistence.contribution_model import MetadataContributionModel
from app.infrastructure.database.session import get_db
from app.shared.domain.exceptions import BusinessRuleViolationError, EntityNotFoundError

router = APIRouter(prefix="/moderation", tags=["Moderation"])

_REVIEWER_ROLES = (Role.CURADOR, Role.MESA_EVALUADORA, Role.ADMINISTRADOR)


async def _require_reviewer(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> int:
    user = await UserRepository(db).get_by_id(user_id)
    if not user or user.role not in _REVIEWER_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso restringido a revisores.")
    return user_id


# ── Schemas ────────────────────────────────────────────────────────────────────

class ModerationStats(BaseModel):
    pending: int
    approved: int
    rejected: int
    total: int


class ContributionQueueItem(BaseModel):
    id: int
    photograph_id: int
    contributor_id: int
    attribute_type: str
    field_name: str
    proposed_value: str
    evidence_notes: Optional[str]
    created_at: Optional[datetime]


class ContributionQueueResponse(BaseModel):
    total: int
    skip: int
    limit: int
    items: List[ContributionQueueItem]


class BatchActionRequest(BaseModel):
    contribution_ids: List[int]
    rejection_reason: Optional[str] = None


class BatchActionResponse(BaseModel):
    processed: int
    failed: int
    errors: List[str]


class RejectRequest(BaseModel):
    rejection_reason: Optional[str] = None


# ── Stats ──────────────────────────────────────────────────────────────────────

@router.get("/stats", response_model=ModerationStats)
async def get_moderation_stats(
    _: int = Depends(_require_reviewer),
    db: AsyncSession = Depends(get_db),
):
    """Contadores de contribuciones por estado."""
    result = await db.execute(
        select(MetadataContributionModel.status, func.count(MetadataContributionModel.id))
        .group_by(MetadataContributionModel.status)
    )
    counts = {row[0]: row[1] for row in result.all()}

    pending = counts.get(ContributionStatus.PENDING, 0)
    approved = counts.get(ContributionStatus.APPROVED, 0)
    rejected = counts.get(ContributionStatus.REJECTED, 0)

    return ModerationStats(
        pending=pending,
        approved=approved,
        rejected=rejected,
        total=pending + approved + rejected,
    )


# ── Queue ──────────────────────────────────────────────────────────────────────

@router.get("/queue", response_model=ContributionQueueResponse)
async def get_moderation_queue(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    attribute_type: Optional[ContributionAttributeType] = Query(None),
    _: int = Depends(_require_reviewer),
    db: AsyncSession = Depends(get_db),
):
    """Cola de contribuciones PENDING ordenadas por fecha de creación (más antiguas primero)."""
    repo = ContributionRepository(db)

    q = select(MetadataContributionModel).where(
        MetadataContributionModel.status == ContributionStatus.PENDING
    )
    if attribute_type:
        q = q.where(MetadataContributionModel.attribute_type == attribute_type)
    q = q.order_by(MetadataContributionModel.created_at.asc()).offset(skip).limit(limit)

    result = await db.execute(q)
    models = result.scalars().all()

    count_q = select(func.count(MetadataContributionModel.id)).where(
        MetadataContributionModel.status == ContributionStatus.PENDING
    )
    if attribute_type:
        count_q = count_q.where(MetadataContributionModel.attribute_type == attribute_type)
    total_result = await db.execute(count_q)
    total = total_result.scalar_one()

    return ContributionQueueResponse(
        total=total,
        skip=skip,
        limit=limit,
        items=[
            ContributionQueueItem(
                id=m.id,
                photograph_id=m.photograph_id,
                contributor_id=m.contributor_id,
                attribute_type=m.attribute_type,
                field_name=m.field_name,
                proposed_value=m.proposed_value,
                evidence_notes=m.evidence_notes,
                created_at=m.created_at,
            )
            for m in models
        ],
    )


# ── Individual approve / reject ────────────────────────────────────────────────

@router.post("/contributions/{contribution_id}/approve", status_code=status.HTTP_200_OK)
async def approve_contribution(
    contribution_id: int,
    reviewer_id: int = Depends(_require_reviewer),
    db: AsyncSession = Depends(get_db),
):
    """Aprueba una contribución individual."""
    try:
        repo = ContributionRepository(db)
        usecase = ApproveContributionUseCase(repo, db)
        contribution = await usecase.execute(contribution_id=contribution_id, reviewer_id=reviewer_id)
        return {"id": contribution.id, "status": contribution.status.value}
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BusinessRuleViolationError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/contributions/{contribution_id}/reject", status_code=status.HTTP_200_OK)
async def reject_contribution(
    contribution_id: int,
    request: RejectRequest,
    reviewer_id: int = Depends(_require_reviewer),
    db: AsyncSession = Depends(get_db),
):
    """Rechaza una contribución individual."""
    try:
        repo = ContributionRepository(db)
        usecase = RejectContributionUseCase(repo)
        contribution = await usecase.execute(
            contribution_id=contribution_id,
            reviewer_id=reviewer_id,
            rejection_reason=request.rejection_reason,
        )
        return {"id": contribution.id, "status": contribution.status.value}
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BusinessRuleViolationError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


# ── Batch operations ───────────────────────────────────────────────────────────

@router.post("/contributions/batch-approve", response_model=BatchActionResponse)
async def batch_approve(
    request: BatchActionRequest,
    reviewer_id: int = Depends(_require_reviewer),
    db: AsyncSession = Depends(get_db),
):
    """Aprueba múltiples contribuciones en una sola operación."""
    processed, failed, errors = 0, 0, []
    repo = ContributionRepository(db)
    usecase = ApproveContributionUseCase(repo, db)

    for cid in request.contribution_ids:
        try:
            await usecase.execute(contribution_id=cid, reviewer_id=reviewer_id)
            processed += 1
        except Exception as e:
            failed += 1
            errors.append(f"#{cid}: {str(e)}")

    return BatchActionResponse(processed=processed, failed=failed, errors=errors)


@router.post("/contributions/batch-reject", response_model=BatchActionResponse)
async def batch_reject(
    request: BatchActionRequest,
    reviewer_id: int = Depends(_require_reviewer),
    db: AsyncSession = Depends(get_db),
):
    """Rechaza múltiples contribuciones en una sola operación."""
    processed, failed, errors = 0, 0, []
    repo = ContributionRepository(db)
    usecase = RejectContributionUseCase(repo)

    for cid in request.contribution_ids:
        try:
            await usecase.execute(
                contribution_id=cid,
                reviewer_id=reviewer_id,
                rejection_reason=request.rejection_reason,
            )
            processed += 1
        except Exception as e:
            failed += 1
            errors.append(f"#{cid}: {str(e)}")

    return BatchActionResponse(processed=processed, failed=failed, errors=errors)
