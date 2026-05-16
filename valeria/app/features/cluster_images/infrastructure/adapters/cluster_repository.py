from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.features.cluster_images.domain.cluster import (
    Cluster, ClusterAlgorithm, ClusteringJob, ClusterStatus,
)
from app.features.cluster_images.domain.cluster_port import IClusterRepository
from app.features.cluster_images.infrastructure.persistence.cluster_model import (
    ClusteringJobModel, ClusterModel,
)


class ClusterRepository(IClusterRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, job: ClusteringJob) -> ClusteringJob:
        job_model = ClusteringJobModel(
            algorithm=ClusterAlgorithm(job.algorithm),
            embedding_model=job.embedding_model,
            n_clusters=job.n_clusters,
            noise_count=job.noise_count,
            processing_time_ms=job.processing_time_ms,
            photograph_ids=job.photograph_ids,
            status=ClusterStatus(job.status),
        )
        self.session.add(job_model)
        await self.session.flush()
        await self.session.refresh(job_model)

        cluster_models = []
        for cluster in job.clusters:
            c_model = ClusterModel(
                job_id=job_model.id,
                label=cluster.label,
                algorithm=ClusterAlgorithm(cluster.algorithm),
                embedding_model=cluster.embedding_model,
                member_count=cluster.member_count,
                centroid_photograph_id=cluster.centroid_photograph_id,
                photograph_ids=cluster.photograph_ids,
                status=ClusterStatus(cluster.status),
            )
            self.session.add(c_model)
            cluster_models.append(c_model)

        await self.session.flush()

        job.id = job_model.id
        job.created_at = job_model.created_at
        job.updated_at = job_model.updated_at
        for i, c_model in enumerate(cluster_models):
            await self.session.refresh(c_model)
            job.clusters[i].id = c_model.id

        return job

    async def get_by_id(self, job_id: int) -> Optional[ClusteringJob]:
        result = await self.session.execute(
            select(ClusteringJobModel).where(ClusteringJobModel.id == job_id)
        )
        model = result.scalar_one_or_none()
        return await self._to_domain(model) if model else None

    async def list(self, skip: int, limit: int) -> List[ClusteringJob]:
        result = await self.session.execute(
            select(ClusteringJobModel)
            .order_by(ClusteringJobModel.id.desc())
            .offset(skip)
            .limit(limit)
        )
        return [await self._to_domain(m) for m in result.scalars().all()]

    async def delete(self, job_id: int) -> bool:
        result = await self.session.execute(
            select(ClusteringJobModel).where(ClusteringJobModel.id == job_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return False
        await self.session.delete(model)
        await self.session.flush()
        return True

    async def _to_domain(self, model: ClusteringJobModel) -> ClusteringJob:
        clusters_result = await self.session.execute(
            select(ClusterModel).where(ClusterModel.job_id == model.id)
        )
        clusters = [
            Cluster(
                id=c.id,
                photograph_ids=c.photograph_ids or [],
                label=c.label,
                algorithm=ClusterAlgorithm(c.algorithm),
                embedding_model=c.embedding_model,
                member_count=c.member_count,
                centroid_photograph_id=c.centroid_photograph_id,
                status=ClusterStatus(c.status),
            )
            for c in clusters_result.scalars().all()
        ]
        return ClusteringJob(
            id=model.id,
            photograph_ids=model.photograph_ids or [],
            clusters=clusters,
            algorithm=ClusterAlgorithm(model.algorithm),
            embedding_model=model.embedding_model,
            n_clusters=model.n_clusters,
            noise_count=model.noise_count,
            processing_time_ms=model.processing_time_ms or 0,
            status=ClusterStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
