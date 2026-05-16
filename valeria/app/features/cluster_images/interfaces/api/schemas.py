from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ClusterRequest(BaseModel):
    photograph_ids: List[int] = Field(min_length=2, description="IDs de fotografías a agrupar")
    algorithm: str = Field(default="dbscan", description="Algoritmo: dbscan | kmeans")
    n_clusters: Optional[int] = Field(
        default=None,
        description="Número de clusters para KMeans (ignorado en DBSCAN)"
    )
    texts: Optional[List[str]] = Field(
        default=None,
        description="Textos descriptivos por fotografía (mismo orden que photograph_ids). "
                    "Si se omiten, se usa 'fotografía {id}' como representación."
    )


class ClusterResponse(BaseModel):
    id: Optional[int]
    label: str
    algorithm: str
    member_count: int
    centroid_photograph_id: Optional[int]
    photograph_ids: List[int]
    status: str


class ClusteringJobResponse(BaseModel):
    id: Optional[int]
    algorithm: str
    embedding_model: str
    n_clusters: int
    noise_count: int
    processing_time_ms: int
    status: str
    photograph_ids: List[int]
    clusters: List[ClusterResponse]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class ClusteringJobListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    jobs: List[ClusteringJobResponse]
