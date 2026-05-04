"""
Taxonomy repository port for ROGER - Valeria API.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.features.taxonomy.domain.taxonomy import TechnicalMetadata


class ITaxonomyRepository(ABC):

    @abstractmethod
    async def save_technical_metadata(self, record: TechnicalMetadata) -> TechnicalMetadata:
        pass

    @abstractmethod
    async def supersede_active_technical(self, photograph_id: int) -> None:
        """Mark all ACTIVE records for a photograph as SUPERSEDED."""
        pass

    @abstractmethod
    async def get_active_technical(self, photograph_id: int) -> Optional[TechnicalMetadata]:
        pass

    @abstractmethod
    async def list_technical_history(self, photograph_id: int) -> List[TechnicalMetadata]:
        """Return all records (ACTIVE + SUPERSEDED) ordered by id desc."""
        pass
