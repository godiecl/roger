from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.generate_timeline.application.generate_timeline_usecase import GenerateTimelineUseCase
from app.features.generate_timeline.domain.timeline import Timeline
from app.features.generate_timeline.infrastructure.adapters.timeline_generator import TimelineGenerator
from app.features.generate_timeline.infrastructure.adapters.timeline_repository import TimelineRepository
from app.features.generate_timeline.interfaces.api.schemas import (
    ApproveTimelineRequest, GenerateTimelineRequest,
    TimelineEventResponse, TimelineListResponse, TimelineResponse,
)
from app.infrastructure.database.session import get_db
from app.shared.domain.exceptions import EntityNotFoundError

router = APIRouter(prefix="/timelines", tags=["Timelines"])


def _build_usecase(db: AsyncSession) -> GenerateTimelineUseCase:
    return GenerateTimelineUseCase(
        generator=TimelineGenerator(),
        repository=TimelineRepository(db),
    )


@router.post("", response_model=TimelineResponse, status_code=status.HTTP_201_CREATED)
async def generate_timeline(
    request: GenerateTimelineRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Genera la línea de tiempo contextual para una fotografía.

    Sitúa la fotografía en su contexto histórico con tres ejes:
    - **biographical**: vida y viajes de Gerstmann en esa época
    - **historical**: eventos mundiales / latinoamericanos del período
    - **expedition**: detalles del viaje o proyecto fotografiado

    Si ya existe una timeline para la fotografía, la retorna sin re-generar.
    Usa force_regeneration=true para generar una nueva.

    Acepta metadatos opcionales de la fotografía para enriquecer el contexto.
    Cuando el RAG esté poblado, los eventos se enriquecen con fuentes verificadas.
    """
    try:
        usecase = _build_usecase(db)
        timeline = await usecase.execute(
            photograph_id=request.photograph_id,
            photograph_date=request.photograph_date,
            photograph_location=request.photograph_location,
            photograph_description=request.photograph_description,
            detected_objects=request.detected_objects,
            force_regeneration=request.force_regeneration,
        )
        return _to_response(timeline)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/photograph/{photograph_id}", response_model=TimelineResponse)
async def get_timeline_for_photograph(
    photograph_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Retorna la timeline más reciente para una fotografía."""
    repository = TimelineRepository(db)
    timeline = await repository.get_by_photograph(photograph_id)
    if not timeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hay timeline para la fotografía {photograph_id}",
        )
    return _to_response(timeline)


@router.get("/{timeline_id}", response_model=TimelineResponse)
async def get_timeline(
    timeline_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Retorna una timeline por ID."""
    try:
        usecase = _build_usecase(db)
        timeline = await usecase.get(timeline_id)
        return _to_response(timeline)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{timeline_id}/approve", response_model=TimelineResponse)
async def approve_timeline(
    timeline_id: int,
    request: ApproveTimelineRequest,
    db: AsyncSession = Depends(get_db),
):
    """Aprueba una timeline (requiere rol curador o administrador)."""
    try:
        usecase = _build_usecase(db)
        timeline = await usecase.approve(timeline_id, request.approved_by)
        return _to_response(timeline)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("", response_model=TimelineListResponse)
async def list_timelines(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    only_approved: bool = Query(False),
    db: AsyncSession = Depends(get_db),
):
    """Lista timelines con paginación."""
    repository = TimelineRepository(db)
    timelines = await repository.list(skip, limit, only_approved)
    return TimelineListResponse(
        total=len(timelines),
        skip=skip,
        limit=limit,
        timelines=[_to_response(t) for t in timelines],
    )


@router.delete("/{timeline_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_timeline(
    timeline_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Elimina una timeline y todos sus eventos."""
    repository = TimelineRepository(db)
    deleted = await repository.delete(timeline_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Timeline {timeline_id} no encontrada",
        )


def _to_response(timeline: Timeline) -> TimelineResponse:
    return TimelineResponse(
        id=timeline.id,
        photograph_id=timeline.photograph_id,
        context_summary=timeline.context_summary,
        provider=timeline.provider,
        generation_time_ms=timeline.generation_time_ms,
        is_approved=timeline.is_approved,
        approved_by=timeline.approved_by,
        approved_at=timeline.approved_at,
        event_count=len(timeline.events),
        events=[
            TimelineEventResponse(
                id=e.id,
                date_label=e.date_label,
                year=e.year,
                title=e.title,
                description=e.description,
                axis=e.axis.value,
                event_type=e.event_type.value,
                source_type=e.source_type.value,
            )
            for e in timeline.events
        ],
        created_at=timeline.created_at,
        updated_at=timeline.updated_at,
    )
