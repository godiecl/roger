from abc import ABC, abstractmethod
from typing import Any, Dict


class IRogerOrchestrator(ABC):
    @abstractmethod
    async def decide(self, message: str) -> Dict[str, Any]:
        pass


class IVisualDescriptionService(ABC):
    @abstractmethod
    async def describe(self, image_name: str) -> Dict[str, Any]:
        pass


class ISemanticSearchService(ABC):
    @abstractmethod
    async def search(self, query: str, top_k: int = 5) -> Any:
        pass


class IVisualSimilarityService(ABC):
    @abstractmethod
    async def search_similar(self, image_name: str, top_k: int = 5) -> Any:
        pass


class IOCRService(ABC):
    @abstractmethod
    async def analyze(self, image_name: str) -> Dict[str, Any]:
        pass


class IObjectDetectionService(ABC):
    @abstractmethod
    async def detect(self, image_name: str) -> Dict[str, Any]:
        pass


class IDamageAnalysisService(ABC):
    @abstractmethod
    async def analyze(self, image_name: str) -> Dict[str, Any]:
        pass