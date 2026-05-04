"""
FastAPI routes for the contributions feature.

Permissions:
  - Submit: any authenticated user (COLABORADOR or higher)
  - List own contributions: any authenticated user
  - List all / list pending: CURADOR, MESA_EVALUADORA, ADMINISTRADOR
  - Approve / Reject: CURADOR, MESA_EVALUADORA, ADMINISTRADOR
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.authenticate.domain.role import Role
from app.features.authenticate.infrastructure.adapters.user_repository import UserRepository
from app.features.authenticate.interfaces.api.dependencies import get_current_user_id
from app.features.contributions.application.approve_contribution_usecase import ApproveContributionUseCase
from app.features.contributions.application.reject_contribution_usecase import RejectContributionUseCase
from app.features.contributions.application.submit_contribution_usecase import SubmitContributionUseCase
from app.features.contributions.domain.contribution import ContributionAttributeType, ContributionStatus
from app.features.contributions.infrastructure.adapters.contribution_repository import ContributionRepository
from app.features.contributions.interfaces.api.schemas import (
    ContributionCreateRequest,
    ContributionListResponse,
    ContributionResponse,
    RejectRequest,
)
from app.infrastructure.database.session import get_db
from app.shared.domain.exceptions import (
    BusinessRuleViolationError,
    EntityNotFoundError,
    ValidationError,
)

router = APIRouter(prefix="/contributions", tags=["Contributions"])

_REVIEWER_ROLES = (Role.CURADOR, Role.MESA_EVALUADORA, Role.ADMINISTRADOR)


async def _require_reviewer(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> int:
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if not user or user.role not in _REVIEWER_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo curadores y evaluadores pueden revisar contribuciones.",
        )
    return user_id


# ── Submit ────────────────────────────────────────────────────────────────────

@router.post("", response_model=ContributionResponse, status_code=status.HTTP_201_CREATED)
async def submit_contribution(
    request: ContributionCreateRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Submit a metadata contribution for a photograph. Any authenticated user."""
    try:
        repo = ContributionRepository(db)
        usecase = SubmitContributionUseCase(repo)
        contribution = await usecase.execute(
            photograph_id=request.photograph_id,
            contributor_id=user_id,
            attribute_type=request.attribute_type,
            field_name=request.field_name,
            proposed_value=request.proposed_value,
            evidence_notes=request.evidence_notes,
        )
        return ContributionResponse(**contribution.__dict__)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ── List (own) ────────────────────────────────────────────────────────────────

@router.get("/mine", response_model=ContributionListResponse)
async def list_my_contributions(
    status_filter: Optional[ContributionStatus] = Query(None, alias="status"),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """List my own contributions."""
    repo = ContributionRepository(db)
    items = await repo.list_by_contributor(user_id, status=status_filter)
    return ContributionListResponse(total=len(items), contributions=[ContributionResponse(**c.__dict__) for c in items])


# ── List pending (curators) ───────────────────────────────────────────────────

@router.get("/pending", response_model=ContributionListResponse)
async def list_pending_contributions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    _: int = Depends(_require_reviewer),
    db: AsyncSession = Depends(get_db),
):
    """List all PENDING contributions — curator review queue."""
    repo = ContributionRepository(db)
    items = await repo.list_pending(skip=skip, limit=limit)
    return ContributionListResponse(total=len(items), contributions=[ContributionResponse(**c.__dict__) for c in items])


# ── List by photograph ────────────────────────────────────────────────────────

@router.get("/photographs/{photograph_id}", response_model=ContributionListResponse)
async def list_contributions_for_photograph(
    photograph_id: int,
    attribute_type: Optional[ContributionAttributeType] = Query(None),
    status_filter: Optional[ContributionStatus] = Query(None, alias="status"),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    List contributions for a photograph.
    Curators see all; other users see only their own.
    """
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    is_reviewer = user and user.role in _REVIEWER_ROLES

    repo = ContributionRepository(db)
    if is_reviewer:
        items = await repo.list_by_photograph(photograph_id, attribute_type, status_filter)
    else:
        all_items = await repo.list_by_photograph(photograph_id, attribute_type, status_filter)
        items = [c for c in all_items if c.contributor_id == user_id]

    return ContributionListResponse(total=len(items), contributions=[ContributionResponse(**c.__dict__) for c in items])


# ── Get one ───────────────────────────────────────────────────────────────────

@router.get("/{contribution_id}", response_model=ContributionResponse)
async def get_contribution(
    contribution_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = ContributionRepository(db)
    contribution = await repo.get_by_id(contribution_id)
    if not contribution:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contribución no encontrada.")

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    is_reviewer = user and user.role in _REVIEWER_ROLES

    if not is_reviewer and contribution.contributor_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin acceso a esta contribución.")

    return ContributionResponse(**contribution.__dict__)


# ── Approve ───────────────────────────────────────────────────────────────────

@router.post("/{contribution_id}/approve", response_model=ContributionResponse)
async def approve_contribution(
    contribution_id: int,
    reviewer_id: int = Depends(_require_reviewer),
    db: AsyncSession = Depends(get_db),
):
    """Approve a contribution — writes the value to the corresponding attribute table."""
    try:
        repo = ContributionRepository(db)
        usecase = ApproveContributionUseCase(repo, db)
        contribution = await usecase.execute(contribution_id=contribution_id, reviewer_id=reviewer_id)
        return ContributionResponse(**contribution.__dict__)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BusinessRuleViolationError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


# ── Reject ────────────────────────────────────────────────────────────────────

@router.post("/{contribution_id}/reject", response_model=ContributionResponse)
async def reject_contribution(
    contribution_id: int,
    request: RejectRequest,
    reviewer_id: int = Depends(_require_reviewer),
    db: AsyncSession = Depends(get_db),
):
    """Reject a contribution."""
    try:
        repo = ContributionRepository(db)
        usecase = RejectContributionUseCase(repo)
        contribution = await usecase.execute(
            contribution_id=contribution_id,
            reviewer_id=reviewer_id,
            rejection_reason=request.rejection_reason,
        )
        return ContributionResponse(**contribution.__dict__)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BusinessRuleViolationError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
