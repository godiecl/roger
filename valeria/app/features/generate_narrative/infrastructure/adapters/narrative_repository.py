"""
Narrative repository adapter implementation
"""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.generate_narrative.domain.narrative_port import NarrativeRepositoryPort
from app.features.generate_narrative.domain.narrative import Narrative
from app.features.generate_narrative.domain.trazabilidad import Trazabilidad, Source, SourceType
from app.features.generate_narrative.infrastructure.persistence.narrative_model import NarrativeModel


class NarrativeRepository(NarrativeRepositoryPort):
    """
    Repository adapter for narrative persistence.
    """

    def __init__(self, db_session: AsyncSession):
        """
        Initialize the repository.

        Args:
            db_session: Database session
        """
        self.db_session = db_session

    async def create(self, narrative: Narrative) -> Narrative:
        """Create a new narrative."""
        model = self._entity_to_model(narrative)
        self.db_session.add(model)
        await self.db_session.flush()
        await self.db_session.refresh(model)
        return self._model_to_entity(model)

    async def get_by_id(self, narrative_id: int) -> Optional[Narrative]:
        """Get a narrative by ID."""
        stmt = select(NarrativeModel).where(NarrativeModel.id == narrative_id)
        result = await self.db_session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def get_by_image_id(
        self,
        image_id: int,
        only_approved: bool = False
    ) -> List[Narrative]:
        """Get all narratives for an image."""
        stmt = select(NarrativeModel).where(NarrativeModel.image_id == image_id)

        if only_approved:
            stmt = stmt.where(NarrativeModel.is_approved == True)

        stmt = stmt.order_by(NarrativeModel.created_at.desc())

        result = await self.db_session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    async def update(self, narrative: Narrative) -> Narrative:
        """Update an existing narrative."""
        stmt = select(NarrativeModel).where(NarrativeModel.id == narrative.id)
        result = await self.db_session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            raise ValueError(f"Narrative {narrative.id} not found")

        # Update fields
        model.text = narrative.text
        model.trazabilidad = self._trazabilidad_to_dict(narrative.trazabilidad)
        model.prompt = narrative.prompt
        model.language = narrative.language
        model.model_used = narrative.model_used
        model.generation_time_ms = narrative.generation_time_ms
        model.is_approved = narrative.is_approved
        model.approved_by = narrative.approved_by
        model.approved_at = narrative.approved_at

        await self.db_session.flush()
        await self.db_session.refresh(model)
        return self._model_to_entity(model)

    async def delete(self, narrative_id: int) -> bool:
        """Delete a narrative."""
        stmt = select(NarrativeModel).where(NarrativeModel.id == narrative_id)
        result = await self.db_session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return False

        await self.db_session.delete(model)
        await self.db_session.flush()
        return True

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        only_approved: bool = False
    ) -> List[Narrative]:
        """List narratives with pagination."""
        stmt = select(NarrativeModel)

        if only_approved:
            stmt = stmt.where(NarrativeModel.is_approved == True)

        stmt = stmt.order_by(NarrativeModel.created_at.desc())
        stmt = stmt.offset(skip).limit(limit)

        result = await self.db_session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    def _entity_to_model(self, narrative: Narrative) -> NarrativeModel:
        """Convert domain entity to SQLAlchemy model."""
        return NarrativeModel(
            id=narrative.id,
            image_id=narrative.image_id,
            text=narrative.text,
            trazabilidad=self._trazabilidad_to_dict(narrative.trazabilidad),
            user_id=narrative.user_id,
            prompt=narrative.prompt,
            language=narrative.language,
            model_used=narrative.model_used,
            generation_time_ms=narrative.generation_time_ms,
            is_approved=narrative.is_approved,
            approved_by=narrative.approved_by,
            approved_at=narrative.approved_at,
            created_at=narrative.created_at,
            updated_at=narrative.updated_at
        )

    def _model_to_entity(self, model: NarrativeModel) -> Narrative:
        """Convert SQLAlchemy model to domain entity."""
        trazabilidad = self._dict_to_trazabilidad(model.trazabilidad)

        return Narrative(
            id=model.id,
            image_id=model.image_id,
            text=model.text,
            trazabilidad=trazabilidad,
            user_id=model.user_id,
            prompt=model.prompt,
            language=model.language,
            model_used=model.model_used,
            generation_time_ms=model.generation_time_ms,
            is_approved=model.is_approved,
            approved_by=model.approved_by,
            approved_at=model.approved_at,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def _trazabilidad_to_dict(self, trazabilidad: Trazabilidad) -> dict:
        """Convert Trazabilidad to dictionary for JSON storage."""
        return {
            "sources": [
                {
                    "text": s.text,
                    "source_type": s.source_type.value,
                    "reference": s.reference,
                    "relevance_score": s.relevance_score
                }
                for s in trazabilidad.sources
            ],
            "primary_source_type": trazabilidad.primary_source_type.value,
            "confidence_score": trazabilidad.confidence_score
        }

    def _dict_to_trazabilidad(self, data: dict) -> Trazabilidad:
        """Convert dictionary to Trazabilidad object."""
        sources = [
            Source(
                text=s["text"],
                source_type=SourceType(s["source_type"]),
                reference=s.get("reference"),
                relevance_score=s.get("relevance_score")
            )
            for s in data["sources"]
        ]

        return Trazabilidad(
            sources=sources,
            primary_source_type=SourceType(data["primary_source_type"]),
            confidence_score=data["confidence_score"]
        )
