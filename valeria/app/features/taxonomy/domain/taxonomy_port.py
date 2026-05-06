"""
Taxonomy repository port for ROGER - Valeria API.
Covers Attributes 01-04: Technical, Chronology, Geographic, Environmental.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.features.taxonomy.domain.taxonomy import (
    TechnicalMetadata,
    ChronologyDating,
    GeographicReference,
    EnvironmentalSpatial,
)


class ITaxonomyRepository(ABC):

    # ── Attribute 01 — Technical Metadata ────────────────────────────────────

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

    # ── Attribute 02 — Chronological Dating ──────────────────────────────────

    @abstractmethod
    async def save_chronology(self, record: ChronologyDating) -> ChronologyDating:
        pass

    @abstractmethod
    async def supersede_active_chronology(self, photograph_id: int) -> None:
        pass

    @abstractmethod
    async def get_active_chronology(self, photograph_id: int) -> Optional[ChronologyDating]:
        pass

    @abstractmethod
    async def list_chronology_history(self, photograph_id: int) -> List[ChronologyDating]:
        pass

    # ── Attribute 03 — Geographic Reference ──────────────────────────────────

    @abstractmethod
    async def save_geographic(self, record: GeographicReference) -> GeographicReference:
        pass

    @abstractmethod
    async def supersede_active_geographic(self, photograph_id: int) -> None:
        pass

    @abstractmethod
    async def get_active_geographic(self, photograph_id: int) -> Optional[GeographicReference]:
        pass

    @abstractmethod
    async def list_geographic_history(self, photograph_id: int) -> List[GeographicReference]:
        pass

    # ── Attribute 04 — Environmental & Spatial Context ───────────────────────

    @abstractmethod
    async def save_environmental(self, record: EnvironmentalSpatial) -> EnvironmentalSpatial:
        pass

    @abstractmethod
    async def supersede_active_environmental(self, photograph_id: int) -> None:
        pass

    @abstractmethod
    async def get_active_environmental(
        self, photograph_id: int
    ) -> Optional[EnvironmentalSpatial]:
        pass

    @abstractmethod
    async def list_environmental_history(
        self, photograph_id: int
    ) -> List[EnvironmentalSpatial]:
        pass
