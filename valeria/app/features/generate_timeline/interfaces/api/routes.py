from datetime import datetime
from statistics import median
from typing import Dict, List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.features.authenticate.interfaces.api.dependencies import get_current_user_id
from app.features.cluster_images.infrastructure.adapters.cluster_repository import ClusterRepository
from app.features.generate_timeline.application.generate_timeline_usecase import GenerateTimelineUseCase
from app.features.generate_timeline.domain.date_resolution import DateResolution
from app.features.generate_timeline.domain.timeline import (
    CollectionClusterSummary, CollectionNarrative, Timeline,
)
from app.features.generate_timeline.infrastructure.adapters.collection_narrative_generator import (
    CollectionNarrativeGenerator,
)
from app.features.generate_timeline.infrastructure.adapters.date_resolver import DateResolver
from app.features.generate_timeline.infrastructure.adapters.timeline_generator import TimelineGenerator
from app.features.generate_timeline.infrastructure.adapters.timeline_repository import TimelineRepository
from app.features.generate_timeline.infrastructure.adapters.wikipedia_enricher import WikipediaEnricher
from app.features.generate_timeline.interfaces.api.schemas import (
    ApproveTimelineRequest, CollectionClusterSummaryResponse,
    CollectionNarrativeResponse, GenerateTimelineRequest,
    TimelineEventResponse, TimelineListResponse, TimelineResponse,
)
from app.features.taxonomy.infrastructure.persistence.taxonomy_model import (
    AttrChronologyDatingModel, AttributeStatus,
)
from app.infrastructure.database.session import get_db
from app.shared.domain.exceptions import EntityNotFoundError

logger = structlog.get_logger()

router = APIRouter(prefix="/timelines", tags=["Timelines"])


def _build_usecase(db: AsyncSession) -> GenerateTimelineUseCase:
    return GenerateTimelineUseCase(
        generator=TimelineGenerator(),
        repository=TimelineRepository(db),
        date_resolver=DateResolver(db),
        wikipedia_enricher=WikipediaEnricher(),
    )


@router.post(
    "/collection/{job_id}",
    response_model=CollectionNarrativeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_collection_narrative(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    _user_id: int = Depends(get_current_user_id),
):
    """
    Genera una narrativa temporal unificada para la colección de fotografías
    de un clustering job.

    Pasos:
    1. Carga el job con sus clusters y photograph_ids.
    2. Resuelve la fecha estimada de cada fotografía desde attr_chronology_dating.
    3. Ordena los clusters por año representativo (mediana de sus fotografías).
    4. Llama al LLM para generar una narrativa cohesiva del corpus completo.

    Requiere autenticación.
    """
    cluster_repo = ClusterRepository(db)
    job = await cluster_repo.get_by_id(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clustering job {job_id} no encontrado",
        )
    if not job.clusters:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"El job {job_id} no tiene clusters",
        )

    all_photo_ids = list({pid for c in job.clusters for pid in c.photograph_ids})
    photo_years = await _bulk_resolve_years(db, all_photo_ids)

    ordered_clusters = _build_ordered_clusters(job.clusters, photo_years)

    generator = CollectionNarrativeGenerator()
    narrative = await generator.generate(
        job_id=job_id,
        ordered_clusters=ordered_clusters,
        photograph_count=len(all_photo_ids),
    )

    logger.info(
        "Narrativa de colección generada",
        job_id=job_id,
        clusters=len(ordered_clusters),
        photographs=len(all_photo_ids),
        provider=narrative.provider,
        ms=narrative.generation_time_ms,
    )

    return _to_collection_response(narrative)


async def _bulk_resolve_years(
    db: AsyncSession,
    photograph_ids: List[int],
) -> Dict[int, Optional[int]]:
    """
    Consulta attr_chronology_dating (status=ACTIVE) para un conjunto de fotografías
    y retorna {photograph_id: year_estimate}.  Un solo query en vez de N.
    """
    if not photograph_ids:
        return {}

    result = await db.execute(
        select(
            AttrChronologyDatingModel.photograph_id,
            AttrChronologyDatingModel.precise_date,
            AttrChronologyDatingModel.date_from,
            AttrChronologyDatingModel.date_to,
        ).where(
            AttrChronologyDatingModel.photograph_id.in_(photograph_ids),
            AttrChronologyDatingModel.status == AttributeStatus.ACTIVE,
        )
    )
    rows = result.all()

    years: Dict[int, Optional[int]] = {pid: None for pid in photograph_ids}
    for row in rows:
        pid = row.photograph_id
        year = None
        if row.precise_date:
            year = row.precise_date.year
        elif row.date_from:
            year_from = row.date_from.year
            year_to = row.date_to.year if row.date_to else year_from
            year = (year_from + year_to) // 2
        if year:
            years[pid] = year
    return years


def _build_ordered_clusters(
    clusters,
    photo_years: Dict[int, Optional[int]],
) -> List[CollectionClusterSummary]:
    summaries = []
    for cluster in clusters:
        resolved = [photo_years.get(pid) for pid in cluster.photograph_ids if photo_years.get(pid)]
        if resolved:
            year_rep = int(median(resolved))
            year_min = min(resolved)
            year_max = max(resolved)
            date_source = "metadata"
        else:
            year_rep = None
            year_min = None
            year_max = None
            date_source = "none"

        summaries.append(CollectionClusterSummary(
            cluster_id=cluster.id,
            label=cluster.label,
            photograph_count=len(cluster.photograph_ids),
            centroid_photograph_id=cluster.centroid_photograph_id,
            year_representative=year_rep,
            year_min=year_min,
            year_max=year_max,
            date_source=date_source,
        ))

    dated = [s for s in summaries if s.year_representative is not None]
    undated = [s for s in summaries if s.year_representative is None]
    dated.sort(key=lambda s: s.year_representative)
    return dated + undated


def _to_collection_response(narrative: CollectionNarrative) -> CollectionNarrativeResponse:
    return CollectionNarrativeResponse(
        job_id=narrative.job_id,
        collection_narrative=narrative.collection_narrative,
        temporal_arc=narrative.temporal_arc,
        thematic_threads=narrative.thematic_threads,
        historical_significance=narrative.historical_significance,
        ordered_clusters=[
            CollectionClusterSummaryResponse(
                cluster_id=c.cluster_id,
                label=c.label,
                photograph_count=c.photograph_count,
                centroid_photograph_id=c.centroid_photograph_id,
                year_representative=c.year_representative,
                year_min=c.year_min,
                year_max=c.year_max,
                date_source=c.date_source,
            )
            for c in narrative.ordered_clusters
        ],
        photograph_count=narrative.photograph_count,
        cluster_count=len(narrative.ordered_clusters),
        year_min=narrative.year_min,
        year_max=narrative.year_max,
        provider=narrative.provider,
        generation_time_ms=narrative.generation_time_ms,
        created_at=narrative.created_at or datetime.utcnow(),
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


@router.get("/wikipedia/{year}", response_model=List[TimelineEventResponse])
async def get_wikipedia_events(
    year: int = Path(..., ge=1800, le=2100),
):
    """Retorna eventos históricos de Wikipedia para un año específico."""
    enricher = WikipediaEnricher()
    resolution = DateResolution(
        year_min=year,
        year_max=year,
        source="metadata",
        confidence=1.0,
    )
    events = await enricher.enrich(resolution)
    return [
        TimelineEventResponse(
            id=None,
            date_label=e.date_label,
            year=e.year,
            title=e.title,
            description=e.description,
            axis=e.axis.value,
            event_type=e.event_type.value,
            source_type=e.source_type.value,
        )
        for e in events
    ]


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
