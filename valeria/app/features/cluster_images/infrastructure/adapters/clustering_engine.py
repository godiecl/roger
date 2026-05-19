"""
ClusteringEngine — agrupa fotografías por similitud visual (CLIP) o textual (fallback).

Pipeline:
  1. Si hay image_paths válidos en disco → CLIP ViT-B/32 (CNN transfer learning visual).
     Satisface FONDEF Hito 3: "clustering de imágenes basado en arquitecturas CNN / transfer learning".
  2. Si open-clip-torch no está instalado o las imágenes no están en disco → sentence-transformers.
  3. Aplica DBSCAN (eps adaptativo k-NN) o KMeans sobre los embeddings.
  4. Identifica la fotografía centroide de cada cluster.

Dependencias CLIP: pip install open-clip-torch torch Pillow  (requirements-analyzers.txt)
"""

import os
import time
from typing import List, Optional

import numpy as np
import structlog

from app.features.cluster_images.domain.cluster import (
    Cluster, ClusterAlgorithm, ClusteringJob, ClusterStatus,
)
from app.features.cluster_images.domain.cluster_port import IClusteringEngine

logger = structlog.get_logger()

_TEXT_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
_CLIP_MODEL_NAME = "open_clip/ViT-B-32"
_CLIP_VALID_THRESHOLD = 0.5


class ClusteringEngine(IClusteringEngine):
    """
    Motor de clustering híbrido: CLIP visual (primario) + sentence-transformers (fallback texto).
    CLIP se activa automáticamente cuando ≥50% de los image_paths existen en disco.
    """

    def __init__(self):
        self._text_model = None
        self._clip_model = None
        self._clip_preprocess = None
        self._using_clip = False

    def _get_text_model(self):
        if self._text_model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._text_model = SentenceTransformer(_TEXT_MODEL_NAME)
                logger.info("SentenceTransformer cargado", model=_TEXT_MODEL_NAME)
            except ImportError:
                raise RuntimeError(
                    "sentence-transformers no está instalado. "
                    "Ejecuta: pip install sentence-transformers"
                )
        return self._text_model

    def _load_clip(self):
        if self._clip_model is None:
            import open_clip
            self._clip_model, _, self._clip_preprocess = open_clip.create_model_and_transforms(
                "ViT-B-32", pretrained="openai"
            )
            self._clip_model.eval()
            logger.info("CLIP model cargado", model=_CLIP_MODEL_NAME)
        return self._clip_model, self._clip_preprocess

    @property
    def embedding_model_name(self) -> str:
        return _CLIP_MODEL_NAME if self._using_clip else _TEXT_MODEL_NAME

    async def cluster(
        self,
        photograph_ids: List[int],
        image_paths: List[Optional[str]],
        algorithm: ClusterAlgorithm,
        n_clusters: Optional[int],
        texts: Optional[List[str]] = None,
    ) -> ClusteringJob:
        start = time.time()

        if len(photograph_ids) < 2:
            raise ValueError("Se necesitan al menos 2 fotografías para realizar clustering")

        try:
            embeddings = self._generate_embeddings(texts or photograph_ids, image_paths)
            cluster_labels = self._run_algorithm(embeddings, algorithm, n_clusters, len(photograph_ids))
            clusters = self._build_clusters(photograph_ids, embeddings, cluster_labels, algorithm)
            unique_labels = set(l for l in cluster_labels if l != -1)
            noise_count = sum(1 for l in cluster_labels if l == -1)
            status = ClusterStatus.COMPLETED
        except Exception as e:
            logger.error("Clustering fallido", error=str(e))
            clusters = []
            unique_labels = set()
            noise_count = 0
            status = ClusterStatus.FAILED

        return ClusteringJob(
            photograph_ids=photograph_ids,
            clusters=clusters,
            algorithm=algorithm,
            embedding_model=self.embedding_model_name,
            n_clusters=len(unique_labels),
            noise_count=noise_count,
            processing_time_ms=int((time.time() - start) * 1000),
            status=status,
        )

    def _generate_embeddings(self, texts, image_paths: List[Optional[str]]) -> np.ndarray:
        clip_embeddings = self._try_clip_embeddings(image_paths)
        if clip_embeddings is not None:
            self._using_clip = True
            return clip_embeddings

        self._using_clip = False
        model = self._get_text_model()
        text_inputs = []
        for i, t in enumerate(texts):
            if isinstance(t, int):
                text_inputs.append(f"fotografía {t}")
            else:
                text_inputs.append(str(t) if t else f"fotografía {i}")
        return model.encode(text_inputs, convert_to_numpy=True, show_progress_bar=False)

    def _try_clip_embeddings(self, image_paths: List[Optional[str]]) -> Optional[np.ndarray]:
        """
        Genera embeddings CLIP (512-dim, ViT-B/32) si ≥50% de los paths son accesibles.
        Retorna None si open-clip-torch no está instalado o no hay suficientes imágenes.
        """
        try:
            from PIL import Image
            import torch

            valid_indices = [
                i for i, p in enumerate(image_paths)
                if p and os.path.isfile(p)
            ]

            if len(valid_indices) < max(2, int(len(image_paths) * _CLIP_VALID_THRESHOLD)):
                logger.info(
                    "CLIP no activado: imágenes insuficientes en disco",
                    valid=len(valid_indices),
                    total=len(image_paths),
                )
                return None

            model, preprocess = self._load_clip()
            dim = 512
            embeddings = np.zeros((len(image_paths), dim), dtype=np.float32)

            for i in valid_indices:
                img_tensor = preprocess(
                    Image.open(image_paths[i]).convert("RGB")
                ).unsqueeze(0)
                with torch.no_grad():
                    feat = model.encode_image(img_tensor)
                    feat = feat / feat.norm(dim=-1, keepdim=True)
                embeddings[i] = feat.cpu().numpy().astype(np.float32)

            if len(valid_indices) < len(image_paths):
                mean_emb = embeddings[valid_indices].mean(axis=0)
                missing = [i for i in range(len(image_paths)) if i not in valid_indices]
                for i in missing:
                    embeddings[i] = mean_emb

            logger.info(
                "CLIP embeddings generados",
                valid_images=len(valid_indices),
                total=len(image_paths),
                model=_CLIP_MODEL_NAME,
            )
            return embeddings

        except ImportError:
            logger.info("open-clip-torch no disponible, usando embeddings de texto")
            return None
        except Exception as e:
            logger.warning("CLIP embedding falló, usando embeddings de texto", error=str(e))
            return None

    def _run_algorithm(
        self,
        embeddings: np.ndarray,
        algorithm: ClusterAlgorithm,
        n_clusters: Optional[int],
        n_samples: int,
    ) -> np.ndarray:
        if algorithm == ClusterAlgorithm.DBSCAN:
            from sklearn.cluster import DBSCAN
            from sklearn.neighbors import NearestNeighbors
            from sklearn.preprocessing import normalize

            normed = normalize(embeddings)
            k = max(2, min(n_samples // 10, n_samples - 1))

            # Eps adaptativo: percentil 85 de las distancias al k-ésimo vecino
            nbrs = NearestNeighbors(n_neighbors=k, metric="cosine").fit(normed)
            distances, _ = nbrs.kneighbors(normed)
            kth_dists = np.sort(distances[:, -1])
            eps = float(np.clip(np.percentile(kth_dists, 85), 0.05, 0.8))
            min_samples = max(2, n_samples // 15)

            logger.info("DBSCAN params adaptativos", eps=round(eps, 3), min_samples=min_samples)
            labels = DBSCAN(eps=eps, min_samples=min_samples, metric="cosine").fit_predict(normed)
        else:
            from sklearn.cluster import KMeans
            k = n_clusters or max(2, int(np.sqrt(n_samples / 2)))
            k = min(k, n_samples - 1)
            labels = KMeans(n_clusters=k, random_state=42, n_init="auto").fit_predict(embeddings)

        return labels

    def _build_clusters(
        self,
        photograph_ids: List[int],
        embeddings: np.ndarray,
        labels: np.ndarray,
        algorithm: ClusterAlgorithm,
    ) -> List[Cluster]:
        unique_labels = sorted(set(l for l in labels if l != -1))
        clusters = []

        for cluster_id in unique_labels:
            mask = labels == cluster_id
            member_ids = [photograph_ids[i] for i, m in enumerate(mask) if m]
            member_embeddings = embeddings[mask]

            centroid = member_embeddings.mean(axis=0)
            distances = np.linalg.norm(member_embeddings - centroid, axis=1)
            centroid_photo_id = member_ids[int(np.argmin(distances))]

            clusters.append(Cluster(
                photograph_ids=member_ids,
                label=f"Grupo {cluster_id + 1}",
                algorithm=algorithm,
                embedding_model=self.embedding_model_name,
                member_count=len(member_ids),
                centroid_photograph_id=centroid_photo_id,
                status=ClusterStatus.COMPLETED,
            ))

        return clusters
