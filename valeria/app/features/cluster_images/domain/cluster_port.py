from abc import ABC, abstractmethod
from typing import List, Optional

from app.features.cluster_images.domain.cluster import ClusterAlgorithm, ClusteringJob


class IClusterRepository(ABC):

    @abstractmethod
    async def create(self, job: ClusteringJob) -> ClusteringJob: ...

    @abstractmethod
    async def get_by_id(self, job_id: int) -> Optional[ClusteringJob]: ...

    @abstractmethod
    async def list(self, skip: int, limit: int) -> List[ClusteringJob]: ...

    @abstractmethod
    async def delete(self, job_id: int) -> bool: ...


class IClusteringEngine(ABC):

    @abstractmethod
    async def cluster(
        self,
        photograph_ids: List[int],
        image_paths: List[Optional[str]],
        algorithm: ClusterAlgorithm,
        n_clusters: Optional[int],
    ) -> ClusteringJob: ...

    @property
    @abstractmethod
    def embedding_model_name(self) -> str: ...
