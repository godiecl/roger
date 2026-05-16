from abc import ABC, abstractmethod
from typing import List, Optional

from app.features.detect_objects.domain.detection import Detection


class IDetectionRepository(ABC):

    @abstractmethod
    async def create(self, detection: Detection) -> Detection: ...

    @abstractmethod
    async def get_by_id(self, detection_id: int) -> Optional[Detection]: ...

    @abstractmethod
    async def get_by_photograph(self, photograph_id: int) -> Optional[Detection]: ...

    @abstractmethod
    async def list(self, skip: int, limit: int) -> List[Detection]: ...

    @abstractmethod
    async def delete(self, detection_id: int) -> bool: ...


class IVisionAnalyzer(ABC):

    @abstractmethod
    async def analyze(
        self,
        photograph_id: int,
        image_path: Optional[str] = None,
        image_url: Optional[str] = None,
    ) -> Detection: ...

    @property
    @abstractmethod
    def provider_name(self) -> str: ...
