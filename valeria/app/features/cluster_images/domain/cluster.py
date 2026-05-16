from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


class ClusterAlgorithm(str, Enum):
    DBSCAN = "dbscan"
    KMEANS = "kmeans"


class ClusterStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ClusterMember:
    photograph_id: int
    similarity_score: float
    id: Optional[int] = None


@dataclass
class Cluster:
    """Agrupación de fotografías por similitud semántica visual."""
    photograph_ids: List[int]
    label: str
    algorithm: ClusterAlgorithm
    embedding_model: str
    member_count: int
    centroid_photograph_id: Optional[int]  # fotografía más representativa del cluster
    status: ClusterStatus = ClusterStatus.COMPLETED
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class ClusteringJob:
    """Resultado de un proceso de clustering sobre un conjunto de fotografías."""
    photograph_ids: List[int]
    clusters: List[Cluster]
    algorithm: ClusterAlgorithm
    embedding_model: str
    n_clusters: int
    noise_count: int       # fotografías que no encajaron en ningún cluster (DBSCAN)
    processing_time_ms: int
    status: ClusterStatus = ClusterStatus.COMPLETED
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
