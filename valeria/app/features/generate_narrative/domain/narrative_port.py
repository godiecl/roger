"""
Port interfaces for narrative operations
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from app.features.generate_narrative.domain.narrative import Narrative


class NarrativeRepositoryPort(ABC):
    """
    Port interface for narrative repository operations.
    """

    @abstractmethod
    async def create(self, narrative: Narrative) -> Narrative:
        """Create a new narrative."""
        pass

    @abstractmethod
    async def get_by_id(self, narrative_id: int) -> Optional[Narrative]:
        """Get a narrative by ID."""
        pass

    @abstractmethod
    async def get_by_image_id(
        self,
        image_id: int,
        only_approved: bool = False
    ) -> List[Narrative]:
        """Get all narratives for an image."""
        pass

    @abstractmethod
    async def update(self, narrative: Narrative) -> Narrative:
        """Update an existing narrative."""
        pass

    @abstractmethod
    async def delete(self, narrative_id: int) -> bool:
        """Delete a narrative."""
        pass

    @abstractmethod
    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        only_approved: bool = False
    ) -> List[Narrative]:
        """List narratives with pagination."""
        pass


class NarrativeGeneratorPort(ABC):
    """
    Port interface for narrative generation operations.
    """

    @abstractmethod
    async def generate(
        self,
        image_id: int,
        prompt: Optional[str] = None,
        language: str = "es",
        user_id: Optional[int] = None
    ) -> Narrative:
        """
        Generate a narrative for an image.

        Args:
            image_id: ID of the image
            prompt: Optional custom prompt
            language: Language for the narrative
            user_id: ID of the user requesting

        Returns:
            Generated Narrative with trazabilidad
        """
        pass

    @abstractmethod
    async def regenerate(
        self,
        narrative_id: int,
        prompt: Optional[str] = None
    ) -> Narrative:
        """
        Regenerate an existing narrative with a new prompt.

        Args:
            narrative_id: ID of the narrative to regenerate
            prompt: New prompt to use

        Returns:
            Regenerated Narrative
        """
        pass
