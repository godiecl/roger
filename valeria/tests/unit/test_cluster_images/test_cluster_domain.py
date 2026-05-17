"""
Unit tests for cluster_images domain entities.
"""

import pytest
from app.features.cluster_images.domain.cluster import (
    Cluster, ClusteringJob, ClusterMember, ClusterAlgorithm, ClusterStatus,
)


def make_cluster(photograph_ids=None, label="Retratos", algorithm=ClusterAlgorithm.DBSCAN):
    ids = photograph_ids or [1, 2, 3]
    return Cluster(
        photograph_ids=ids,
        label=label,
        algorithm=algorithm,
        embedding_model="paraphrase-multilingual-MiniLM-L12-v2",
        member_count=len(ids),
        centroid_photograph_id=ids[0] if ids else None,
    )


def make_job(clusters=None, noise_count=0):
    c = clusters or [make_cluster()]
    all_ids = [pid for cluster in c for pid in cluster.photograph_ids]
    return ClusteringJob(
        photograph_ids=all_ids,
        clusters=c,
        algorithm=ClusterAlgorithm.DBSCAN,
        embedding_model="paraphrase-multilingual-MiniLM-L12-v2",
        n_clusters=len(c),
        noise_count=noise_count,
        processing_time_ms=3500,
    )


class TestClusterAlgorithm:

    def test_enum_values(self):
        assert ClusterAlgorithm.DBSCAN == "dbscan"
        assert ClusterAlgorithm.KMEANS == "kmeans"


class TestClusterStatus:

    def test_enum_values(self):
        assert ClusterStatus.PENDING == "pending"
        assert ClusterStatus.COMPLETED == "completed"
        assert ClusterStatus.FAILED == "failed"


class TestClusterMember:

    def test_create_member(self):
        m = ClusterMember(photograph_id=42, similarity_score=0.87)
        assert m.photograph_id == 42
        assert m.similarity_score == 0.87
        assert m.id is None


class TestCluster:

    def test_create_cluster_with_required_fields(self):
        c = make_cluster(photograph_ids=[10, 11, 12], label="Paisajes")
        assert c.label == "Paisajes"
        assert c.member_count == 3
        assert c.centroid_photograph_id == 10

    def test_default_status_is_completed(self):
        c = make_cluster()
        assert c.status == ClusterStatus.COMPLETED

    def test_cluster_with_kmeans_algorithm(self):
        c = make_cluster(algorithm=ClusterAlgorithm.KMEANS)
        assert c.algorithm == ClusterAlgorithm.KMEANS

    def test_cluster_stores_photograph_ids(self):
        c = make_cluster(photograph_ids=[5, 6, 7, 8])
        assert c.photograph_ids == [5, 6, 7, 8]

    def test_cluster_without_centroid(self):
        c = Cluster(
            photograph_ids=[],
            label="Vacío",
            algorithm=ClusterAlgorithm.DBSCAN,
            embedding_model="model",
            member_count=0,
            centroid_photograph_id=None,
        )
        assert c.centroid_photograph_id is None


class TestClusteringJob:

    def test_create_job_with_single_cluster(self):
        cluster = make_cluster(photograph_ids=[1, 2, 3])
        job = make_job(clusters=[cluster])
        assert job.n_clusters == 1
        assert job.noise_count == 0
        assert job.status == ClusterStatus.COMPLETED

    def test_job_stores_noise_count(self):
        job = make_job(noise_count=5)
        assert job.noise_count == 5

    def test_job_with_multiple_clusters(self):
        c1 = make_cluster(photograph_ids=[1, 2], label="Retratos")
        c2 = make_cluster(photograph_ids=[3, 4], label="Paisajes")
        job = make_job(clusters=[c1, c2])
        assert job.n_clusters == 2
        assert len(job.clusters) == 2

    def test_job_processing_time_stored(self):
        job = make_job()
        assert job.processing_time_ms == 3500
