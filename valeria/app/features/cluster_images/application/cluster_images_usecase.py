from typing import List, Optional

import structlog

from app.features.cluster_images.domain.cluster import ClusterAlgorithm, ClusteringJob
from app.features.cluster_images.domain.cluster_port import IClusterRepository, IClusteringEngine
from app.shared.domain.exceptions import EntityNotFoundError

logger = structlog.get_logger()


class ClusterImagesUseCase:

    def __init__(self, engine: IClusteringEngine, repository: IClusterRepository):
        self.engine = engine
        self.repository = repository

    async def execute(
        self,
        photograph_ids: List[int],
        algorithm: ClusterAlgorithm = ClusterAlgorithm.DBSCAN,
        n_clusters: Optional[int] = None,
        texts: Optional[List[str]] = None,
        image_paths: Optional[List[Optional[str]]] = None,
    ) -> ClusteringJob:
        if len(photograph_ids) < 2:
            raise ValueError("Se necesitan al menos 2 fotografías para realizar clustering")

        logger.info(
            "Iniciando clustering",
            n_photographs=len(photograph_ids),
            algorithm=algorithm.value,
            n_clusters=n_clusters,
        )

        paths = image_paths or [None] * len(photograph_ids)

        job = await self.engine.cluster(
            photograph_ids=photograph_ids,
            image_paths=paths,
            algorithm=algorithm,
            n_clusters=n_clusters,
            texts=texts,
        )

        saved = await self.repository.create(job)

        logger.info(
            "Clustering completado",
            job_id=saved.id,
            n_clusters=saved.n_clusters,
            noise_count=saved.noise_count,
            processing_time_ms=saved.processing_time_ms,
        )

        return saved

    async def get(self, job_id: int) -> ClusteringJob:
        job = await self.repository.get_by_id(job_id)
        if not job:
            raise EntityNotFoundError(f"Job de clustering {job_id} no encontrado.")
        return job

    async def list(self, skip: int, limit: int) -> List[ClusteringJob]:
        return await self.repository.list(skip, limit)
