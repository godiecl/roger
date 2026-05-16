from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, Enum as SQLEnum, JSON

from app.infrastructure.database.base import BaseModel
from app.features.cluster_images.domain.cluster import ClusterAlgorithm, ClusterStatus


def _enum_values(x):
    return [e.value for e in x]


class ClusteringJobModel(BaseModel):
    """Registro de un proceso de clustering completo."""

    __tablename__ = "clustering_jobs"

    algorithm = Column(
        SQLEnum(ClusterAlgorithm, values_callable=_enum_values),
        nullable=False,
    )
    embedding_model = Column(String(150), nullable=False)
    n_clusters = Column(Integer, nullable=False, default=0)
    noise_count = Column(Integer, nullable=False, default=0)
    processing_time_ms = Column(Integer, nullable=True)
    photograph_ids = Column(JSON, nullable=False)  # lista de IDs procesados
    status = Column(
        SQLEnum(ClusterStatus, values_callable=_enum_values),
        nullable=False,
        default=ClusterStatus.COMPLETED,
    )

    def __repr__(self) -> str:
        return f"<ClusteringJobModel(id={self.id}, n_clusters={self.n_clusters}, algorithm={self.algorithm})>"


class ClusterModel(BaseModel):
    """Un cluster individual dentro de un job de clustering."""

    __tablename__ = "clusters"

    job_id = Column(
        Integer, ForeignKey("clustering_jobs.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    label = Column(String(255), nullable=False)
    algorithm = Column(
        SQLEnum(ClusterAlgorithm, values_callable=_enum_values),
        nullable=False,
    )
    embedding_model = Column(String(150), nullable=False)
    member_count = Column(Integer, nullable=False, default=0)
    centroid_photograph_id = Column(Integer, nullable=True)
    photograph_ids = Column(JSON, nullable=False)  # miembros de este cluster
    status = Column(
        SQLEnum(ClusterStatus, values_callable=_enum_values),
        nullable=False,
        default=ClusterStatus.COMPLETED,
    )

    def __repr__(self) -> str:
        return f"<ClusterModel(id={self.id}, label={self.label}, members={self.member_count})>"
