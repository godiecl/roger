from datetime import datetime
from typing import List, Optional

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.features.generate_timeline.domain.timeline import (
    EventType, SourceType, Timeline, TimelineAxis, TimelineEvent,
)
from app.features.generate_timeline.domain.timeline_port import ITimelineRepository
from app.features.generate_timeline.infrastructure.persistence.timeline_model import (
    TimelineEventModel, TimelineModel,
)


class TimelineRepository(ITimelineRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, timeline: Timeline) -> Timeline:
        model = TimelineModel(
            photograph_id=timeline.photograph_id,
            provider=timeline.provider,
            context_summary=timeline.context_summary,
            generation_time_ms=timeline.generation_time_ms,
            is_approved=timeline.is_approved,
            approved_by=timeline.approved_by,
            approved_at=timeline.approved_at,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)

        event_models = []
        for event in timeline.events:
            e_model = TimelineEventModel(
                timeline_id=model.id,
                date_label=event.date_label,
                year=event.year,
                title=event.title,
                description=event.description,
                axis=TimelineAxis(event.axis),
                event_type=EventType(event.event_type),
                source_type=SourceType(event.source_type),
            )
            self.session.add(e_model)
            event_models.append(e_model)

        await self.session.flush()

        timeline.id = model.id
        timeline.created_at = model.created_at
        timeline.updated_at = model.updated_at
        for i, e_model in enumerate(event_models):
            await self.session.refresh(e_model)
            timeline.events[i].id = e_model.id

        return timeline

    async def get_by_id(self, timeline_id: int) -> Optional[Timeline]:
        result = await self.session.execute(
            select(TimelineModel).where(TimelineModel.id == timeline_id)
        )
        model = result.scalar_one_or_none()
        return await self._to_domain(model) if model else None

    async def get_by_photograph(self, photograph_id: int) -> Optional[Timeline]:
        result = await self.session.execute(
            select(TimelineModel)
            .where(TimelineModel.photograph_id == photograph_id)
            .order_by(TimelineModel.id.desc())
            .limit(1)
        )
        model = result.scalar_one_or_none()
        return await self._to_domain(model) if model else None

    async def list(self, skip: int, limit: int, only_approved: bool = False) -> List[Timeline]:
        query = select(TimelineModel).order_by(TimelineModel.id.desc())
        if only_approved:
            query = query.where(TimelineModel.is_approved == True)
        result = await self.session.execute(query.offset(skip).limit(limit))
        return [await self._to_domain(m) for m in result.scalars().all()]

    async def update(self, timeline: Timeline) -> Timeline:
        await self.session.execute(
            update(TimelineModel)
            .where(TimelineModel.id == timeline.id)
            .values(
                is_approved=timeline.is_approved,
                approved_by=timeline.approved_by,
                approved_at=timeline.approved_at,
                context_summary=timeline.context_summary,
            )
        )
        await self.session.flush()
        return timeline

    async def delete(self, timeline_id: int) -> bool:
        result = await self.session.execute(
            select(TimelineModel).where(TimelineModel.id == timeline_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return False
        await self.session.delete(model)
        await self.session.flush()
        return True

    async def _to_domain(self, model: TimelineModel) -> Timeline:
        events_result = await self.session.execute(
            select(TimelineEventModel)
            .where(TimelineEventModel.timeline_id == model.id)
            .order_by(TimelineEventModel.year.asc(), TimelineEventModel.id.asc())
        )
        events = [
            TimelineEvent(
                id=e.id,
                date_label=e.date_label,
                year=e.year,
                title=e.title,
                description=e.description,
                axis=TimelineAxis(e.axis),
                event_type=EventType(e.event_type),
                source_type=SourceType(e.source_type),
            )
            for e in events_result.scalars().all()
        ]
        return Timeline(
            id=model.id,
            photograph_id=model.photograph_id,
            provider=model.provider,
            context_summary=model.context_summary or "",
            generation_time_ms=model.generation_time_ms or 0,
            is_approved=model.is_approved,
            approved_by=model.approved_by,
            approved_at=model.approved_at,
            events=events,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
