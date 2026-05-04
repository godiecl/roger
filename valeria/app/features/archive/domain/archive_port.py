"""
Archive repository port (interface) for ROGER - Valeria API.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.features.archive.domain.archive import Box, Roll, Photograph, PhotographFile


class IArchiveRepository(ABC):

    # ── Boxes ─────────────────────────────────────────────────────────────────

    @abstractmethod
    async def create_box(self, box: Box) -> Box:
        pass

    @abstractmethod
    async def get_box(self, box_id: int) -> Optional[Box]:
        pass

    @abstractmethod
    async def list_boxes(self, collection_id: int, skip: int = 0, limit: int = 100) -> List[Box]:
        pass

    # ── Rolls ─────────────────────────────────────────────────────────────────

    @abstractmethod
    async def create_roll(self, roll: Roll) -> Roll:
        pass

    @abstractmethod
    async def get_roll(self, roll_id: int) -> Optional[Roll]:
        pass

    @abstractmethod
    async def list_rolls(self, box_id: int, skip: int = 0, limit: int = 100) -> List[Roll]:
        pass

    # ── Photographs ───────────────────────────────────────────────────────────

    @abstractmethod
    async def create_photograph(self, photograph: Photograph) -> Photograph:
        pass

    @abstractmethod
    async def get_photograph(self, photograph_id: int) -> Optional[Photograph]:
        pass

    @abstractmethod
    async def list_photographs(self, roll_id: int, skip: int = 0, limit: int = 100) -> List[Photograph]:
        pass

    # ── PhotographFiles ───────────────────────────────────────────────────────

    @abstractmethod
    async def register_file(self, file: PhotographFile) -> PhotographFile:
        pass

    @abstractmethod
    async def list_files(self, photograph_id: int) -> List[PhotographFile]:
        pass
