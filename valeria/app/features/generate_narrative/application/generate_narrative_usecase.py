"""
Use case for generating narratives
"""
import structlog
from typing import Optional

from app.features.generate_narrative.domain.narrative_port import (
    NarrativeGeneratorPort,
    NarrativeRepositoryPort
)
from app.features.generate_narrative.domain.narrative import Narrative

logger = structlog.get_logger()


class GenerateNarrativeUseCase:
    """
    Use case for generating AI-powered narratives about images.
    """

    def __init__(
        self,
        generator: NarrativeGeneratorPort,
        repository: NarrativeRepositoryPort
    ):
        """
        Initialize the use case.

        Args:
            generator: The narrative generator service
            repository: The narrative repository
        """
        self.generator = generator
        self.repository = repository

    async def execute(
        self,
        image_id: int,
        prompt: Optional[str] = None,
        language: str = "es",
        user_id: Optional[int] = None
    ) -> Narrative:
        """
        Generate and save a narrative for an image.

        Args:
            image_id: ID of the image
            prompt: Optional custom prompt
            language: Language for the narrative
            user_id: ID of the user requesting

        Returns:
            Generated and saved Narrative
        """
        logger.info(
            "Generating narrative",
            image_id=image_id,
            language=language,
            has_custom_prompt=bool(prompt)
        )

        # Generate narrative using AI
        narrative = await self.generator.generate(
            image_id=image_id,
            prompt=prompt,
            language=language,
            user_id=user_id
        )

        # Save to repository
        saved_narrative = await self.repository.create(narrative)

        logger.info(
            "Narrative generated and saved",
            narrative_id=saved_narrative.id,
            confidence=saved_narrative.trazabilidad.confidence_score,
            is_verified=saved_narrative.is_verified()
        )

        return saved_narrative

    async def regenerate(
        self,
        narrative_id: int,
        prompt: Optional[str] = None
    ) -> Narrative:
        """
        Regenerate an existing narrative.

        Args:
            narrative_id: ID of the narrative to regenerate
            prompt: New prompt to use

        Returns:
            Regenerated and updated Narrative
        """
        logger.info(
            "Regenerating narrative",
            narrative_id=narrative_id,
            has_new_prompt=bool(prompt)
        )

        # Get existing narrative
        existing = await self.repository.get_by_id(narrative_id)
        if not existing:
            raise ValueError(f"Narrative {narrative_id} not found")

        # Generate new narrative
        new_narrative = await self.generator.generate(
            image_id=existing.image_id,
            prompt=prompt or existing.prompt,
            language=existing.language,
            user_id=existing.user_id
        )

        # Update the existing narrative
        existing.text = new_narrative.text
        existing.trazabilidad = new_narrative.trazabilidad
        existing.prompt = new_narrative.prompt
        existing.model_used = new_narrative.model_used
        existing.generation_time_ms = new_narrative.generation_time_ms
        existing.is_approved = False  # Reset approval on regeneration
        existing.approved_by = None
        existing.approved_at = None

        # Save updated narrative
        updated_narrative = await self.repository.update(existing)

        logger.info(
            "Narrative regenerated",
            narrative_id=updated_narrative.id,
            confidence=updated_narrative.trazabilidad.confidence_score
        )

        return updated_narrative

    async def approve_narrative(
        self,
        narrative_id: int,
        approved_by: int
    ) -> Narrative:
        """
        Approve a narrative.

        Args:
            narrative_id: ID of the narrative
            approved_by: ID of the user approving

        Returns:
            Approved Narrative
        """
        logger.info(
            "Approving narrative",
            narrative_id=narrative_id,
            approved_by=approved_by
        )

        narrative = await self.repository.get_by_id(narrative_id)
        if not narrative:
            raise ValueError(f"Narrative {narrative_id} not found")

        narrative.approve(approved_by)
        updated = await self.repository.update(narrative)

        logger.info("Narrative approved", narrative_id=updated.id)
        return updated

    async def unapprove_narrative(self, narrative_id: int) -> Narrative:
        """
        Unapprove a narrative.

        Args:
            narrative_id: ID of the narrative

        Returns:
            Unapproved Narrative
        """
        logger.info("Unapproving narrative", narrative_id=narrative_id)

        narrative = await self.repository.get_by_id(narrative_id)
        if not narrative:
            raise ValueError(f"Narrative {narrative_id} not found")

        narrative.unapprove()
        updated = await self.repository.update(narrative)

        logger.info("Narrative unapproved", narrative_id=updated.id)
        return updated
