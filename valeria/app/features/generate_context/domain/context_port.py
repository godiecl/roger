from abc import ABC, abstractmethod
from typing import Optional, List
from app.features.generate_context.domain.context import ImageContext


class IContextGenerator(ABC):
    @abstractmethod
    async def generate(
        self,
        image_id: int,
        title: Optional[str],
        description: Optional[str],
        year: Optional[int],
        location: Optional[str],
    ) -> ImageContext:
        ...


class IContextRepository(ABC):
    @abstractmethod
    async def save(self, context: ImageContext) -> ImageContext: ...

    @abstractmethod
    async def get_anchored(self, image_id: int) -> List[ImageContext]: ...

    @abstractmethod
    async def get_by_id(self, context_id: int) -> Optional[ImageContext]: ...

    @abstractmethod
    async def anchor(self, context_id: int, user_id: int) -> ImageContext: ...

    @abstractmethod
    async def unanchor(self, context_id: int) -> ImageContext: ...

    @abstractmethod
    async def toggle_like(self, context_id: int, ip_hash: str) -> tuple[bool, int]:
        """Returns (liked: bool, new_like_count: int)."""
        ...

    @abstractmethod
    async def add_report(self, context_id: int, ip_hash: str, reason: Optional[str]) -> bool:
        """Returns False if already reported (409 case)."""
        ...

    @abstractmethod
    async def list_pending(self, skip: int, limit: int) -> List[ImageContext]: ...

    @abstractmethod
    async def count_pending_reports(self) -> int: ...
