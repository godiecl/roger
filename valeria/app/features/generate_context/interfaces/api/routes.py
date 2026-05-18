import hashlib
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.authenticate.domain.role import Role
from app.features.authenticate.infrastructure.adapters.user_repository import UserRepository
from app.features.authenticate.interfaces.api.dependencies import get_current_user_id
from app.features.generate_context.application.generate_context_usecase import GenerateContextUseCase
from app.features.generate_context.domain.context import ImageContext
from app.features.generate_context.infrastructure.adapters.context_generator import ContextGenerator
from app.features.generate_context.infrastructure.adapters.context_repository import ContextRepository
from app.features.generate_context.interfaces.api.schemas import (
    ContextListResponse,
    ContextResponse,
    LikeResponse,
    PendingReportsCountResponse,
    ReportRequest,
)
from app.infrastructure.database.session import get_db

router = APIRouter(prefix="/context", tags=["Context"])


def _ip_hash(request: Request) -> str:
    ip = request.client.host if request.client else "unknown"
    return hashlib.sha256(ip.encode()).hexdigest()


def _to_response(c: ImageContext) -> ContextResponse:
    return ContextResponse(
        id=c.id,
        image_id=c.image_id,
        text=c.text,
        provider=c.provider,
        generation_time_ms=c.generation_time_ms,
        is_anchored=c.is_anchored,
        anchored_by=c.anchored_by,
        anchored_at=c.anchored_at,
        like_count=c.like_count,
        report_count=c.report_count,
        created_at=c.created_at,
        updated_at=c.updated_at,
    )


async def _require_curator_or_admin(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> int:
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if not user or user.role not in (Role.CURADOR, Role.ADMINISTRADOR):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo curadores y administradores pueden gestionar contextos.",
        )
    return user_id


async def _require_admin(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> int:
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if not user or user.role != Role.ADMINISTRADOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden acceder a esta información.",
        )
    return user_id


# ── Public endpoints ───────────────────────────────────────────────────────────

@router.post("/generate/{image_id}", response_model=ContextResponse, status_code=status.HTTP_201_CREATED)
async def generate_context(
    image_id: int,
    title: Optional[str] = Query(None),
    description: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    location: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Genera un nuevo contexto histórico para la imagen. Siempre crea uno nuevo por visita."""
    try:
        usecase = GenerateContextUseCase(ContextGenerator(), ContextRepository(db))
        context = await usecase.execute(
            image_id=image_id,
            title=title,
            description=description,
            year=year,
            location=location,
        )
        return _to_response(context)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/image/{image_id}/anchored", response_model=ContextListResponse)
async def get_anchored_contexts(
    image_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Retorna los contextos anclados por curador para una imagen."""
    repo = ContextRepository(db)
    contexts = await repo.get_anchored(image_id)
    return ContextListResponse(total=len(contexts), contexts=[_to_response(c) for c in contexts])


@router.post("/{context_id}/like", response_model=LikeResponse)
async def toggle_like(
    context_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Toggle like en un contexto. Limitado a 1 por IP."""
    ip_hash = _ip_hash(request)
    repo = ContextRepository(db)
    try:
        liked, like_count = await repo.toggle_like(context_id, ip_hash)
        return LikeResponse(liked=liked, like_count=like_count)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{context_id}/report", status_code=status.HTTP_204_NO_CONTENT)
async def report_context(
    context_id: int,
    body: ReportRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Reporta un contexto. One-way: 409 si ya fue reportado desde esta IP."""
    ip_hash = _ip_hash(request)
    repo = ContextRepository(db)
    try:
        created = await repo.add_report(context_id, ip_hash, body.reason)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    if not created:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya reportaste este contenido.",
        )


# ── Curator / Admin endpoints ──────────────────────────────────────────────────

@router.post("/{context_id}/anchor", response_model=ContextResponse)
async def anchor_context(
    context_id: int,
    user_id: int = Depends(_require_curator_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """Ancla un contexto para mostrarlo fijo en el viewer."""
    repo = ContextRepository(db)
    try:
        context = await repo.anchor(context_id, user_id)
        return _to_response(context)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{context_id}/anchor", response_model=ContextResponse)
async def unanchor_context(
    context_id: int,
    _: int = Depends(_require_curator_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """Desancla un contexto."""
    repo = ContextRepository(db)
    try:
        context = await repo.unanchor(context_id)
        return _to_response(context)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/pending", response_model=ContextListResponse)
async def list_pending_contexts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    _: int = Depends(_require_curator_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """Lista contextos con likes > 0 pendientes de anclar, ordenados por likes DESC."""
    repo = ContextRepository(db)
    contexts = await repo.list_pending(skip, limit)
    return ContextListResponse(total=len(contexts), contexts=[_to_response(c) for c in contexts])


@router.get("/pending-reports-count", response_model=PendingReportsCountResponse)
async def pending_reports_count(
    _: int = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Total de reportes pendientes de revisión. Para badge en panel admin."""
    repo = ContextRepository(db)
    count = await repo.count_pending_reports()
    return PendingReportsCountResponse(count=count)
