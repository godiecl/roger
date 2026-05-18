from typing import List, Optional

import structlog

from app.features.generate_timeline.domain.timeline import Timeline
from app.features.generate_timeline.domain.timeline_port import ITimelineGenerator, ITimelineRepository
from app.features.generate_timeline.infrastructure.adapters.date_resolver import DateResolver
from app.features.generate_timeline.infrastructure.adapters.wikipedia_enricher import WikipediaEnricher
from app.shared.domain.exceptions import EntityNotFoundError

logger = structlog.get_logger()


class GenerateTimelineUseCase:

    def __init__(
        self,
        generator: ITimelineGenerator,
        repository: ITimelineRepository,
        date_resolver: DateResolver,
        wikipedia_enricher: WikipediaEnricher,
    ):
        self.generator = generator
        self.repository = repository
        self.date_resolver = date_resolver
        self.wikipedia_enricher = wikipedia_enricher

    async def execute(
        self,
        photograph_id: int,
        photograph_date: Optional[str] = None,
        photograph_location: Optional[str] = None,
        photograph_description: Optional[str] = None,
        detected_objects: Optional[List[str]] = None,
        force_regeneration: bool = False,
    ) -> Timeline:
        logger.info("Generando línea de tiempo", photograph_id=photograph_id)

        if not force_regeneration:
            existing = await self.repository.get_by_photograph(photograph_id)
            if existing:
                logger.info("Retornando timeline en caché", timeline_id=existing.id)
                return existing

        rag_context = " ".join(filter(None, [photograph_description, photograph_location]))
        date_resolution = await self.date_resolver.resolve(photograph_id, context=rag_context)
        wikipedia_events = await self.wikipedia_enricher.enrich(date_resolution)

        logger.info(
            "Enriquecimiento Wikipedia",
            photograph_id=photograph_id,
            date_source=date_resolution.source,
            date_label=date_resolution.label if date_resolution.is_resolved else "sin fecha",
            wikipedia_events=len(wikipedia_events),
        )

        timeline = await self.generator.generate(
            photograph_id=photograph_id,
            photograph_date=photograph_date,
            photograph_location=photograph_location,
            photograph_description=photograph_description,
            detected_objects=detected_objects,
            wikipedia_events=wikipedia_events,
        )

        saved = await self.repository.create(timeline)

        logger.info(
            "Timeline generada",
            timeline_id=saved.id,
            event_count=len(saved.events),
            provider=saved.provider,
        )

        return saved

    async def get(self, timeline_id: int) -> Timeline:
        timeline = await self.repository.get_by_id(timeline_id)
        if not timeline:
            raise EntityNotFoundError(f"Timeline {timeline_id} no encontrada.")
        return timeline

    async def get_for_photograph(self, photograph_id: int) -> Optional[Timeline]:
        return await self.repository.get_by_photograph(photograph_id)

    async def approve(self, timeline_id: int, user_id: int) -> Timeline:
        timeline = await self.repository.get_by_id(timeline_id)
        if not timeline:
            raise EntityNotFoundError(f"Timeline {timeline_id} no encontrada.")
        timeline.approve(user_id)
        return await self.repository.update(timeline)

    async def list(self, skip: int, limit: int, only_approved: bool = False) -> List[Timeline]:
        return await self.repository.list(skip, limit, only_approved)
