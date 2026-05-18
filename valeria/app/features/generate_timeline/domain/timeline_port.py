from abc import ABC, abstractmethod
from typing import List, Optional

from app.features.generate_timeline.domain.timeline import Timeline, TimelineEvent


class ITimelineRepository(ABC):

    @abstractmethod
    async def create(self, timeline: Timeline) -> Timeline: ...

    @abstractmethod
    async def get_by_id(self, timeline_id: int) -> Optional[Timeline]: ...

    @abstractmethod
    async def get_by_photograph(self, photograph_id: int) -> Optional[Timeline]: ...

    @abstractmethod
    async def list(self, skip: int, limit: int, only_approved: bool) -> List[Timeline]: ...

    @abstractmethod
    async def update(self, timeline: Timeline) -> Timeline: ...

    @abstractmethod
    async def delete(self, timeline_id: int) -> bool: ...


class ITimelineGenerator(ABC):

    @abstractmethod
    async def generate(
        self,
        photograph_id: int,
        photograph_date: Optional[str],
        photograph_location: Optional[str],
        photograph_description: Optional[str],
        detected_objects: Optional[List[str]],
        wikipedia_events: Optional[List[TimelineEvent]] = None,
    ) -> Timeline: ...

    @property
    @abstractmethod
    def provider_name(self) -> str: ...
