"""
Qdrant vector store implementation para ROGER - Valeria API.

Para entornos de producción. Conserva la interfaz de BaseVectorStore para que
sea intercambiable con ChromaVectorStore vía VectorStoreFactory.

Instalación (descomentar en requirements.txt y reinstalar):
    qdrant-client>=1.12.0

Configuración (en .env / .env.prod):
    VECTOR_STORE_PROVIDER=qdrant
    QDRANT_URL=http://qdrant:6333         # dentro de docker compose
    QDRANT_API_KEY=<api-key>              # obligatorio si el server lo exige

Para activarlo en el factory, ver
docs interno en `vector_stores/README.prod.md`.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np

from app.infrastructure.rag.vector_stores.base_vector_store import BaseVectorStore
from app.config.settings import settings

try:
    from qdrant_client import AsyncQdrantClient
    from qdrant_client.http import models as qmodels
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    AsyncQdrantClient = None  # type: ignore
    qmodels = None             # type: ignore


_DEFAULT_DIM = 384  # all-MiniLM-L6-v2 / multilingual MiniLM. Ajustar si cambia el embedder.


class QdrantVectorStore(BaseVectorStore):
    """Adaptador Qdrant compatible con BaseVectorStore."""

    def __init__(
        self,
        collection_name: str = "default",
        vector_size: int = _DEFAULT_DIM,
        distance: str = "cosine",
    ) -> None:
        if not QDRANT_AVAILABLE:
            raise ImportError(
                "qdrant-client no está instalado. Agregar 'qdrant-client>=1.12.0' "
                "a requirements.txt y reinstalar."
            )

        url = settings.qdrant_url or "http://localhost:6333"
        api_key = settings.qdrant_api_key

        self.collection_name = collection_name
        self.vector_size = vector_size
        self._distance = self._parse_distance(distance)

        self.client: AsyncQdrantClient = AsyncQdrantClient(
            url=url,
            api_key=api_key,
            prefer_grpc=False,   # grpc requiere puerto extra; HTTP es suficiente para el MVP
            timeout=30,
        )
        self._collection_ready = False

    # ── Helpers internos ──────────────────────────────────────────────────────

    @staticmethod
    def _parse_distance(name: str) -> "qmodels.Distance":
        n = name.lower()
        if n == "cosine":
            return qmodels.Distance.COSINE
        if n in {"dot", "dot_product"}:
            return qmodels.Distance.DOT
        if n in {"euclid", "euclidean", "l2"}:
            return qmodels.Distance.EUCLID
        raise ValueError(f"Distance no soportada: {name}")

    async def _ensure_collection(self) -> None:
        """Crea la colección la primera vez. Idempotente."""
        if self._collection_ready:
            return
        existing = await self.client.get_collections()
        if not any(c.name == self.collection_name for c in existing.collections):
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=qmodels.VectorParams(
                    size=self.vector_size,
                    distance=self._distance,
                ),
            )
        self._collection_ready = True

    @staticmethod
    def _to_qdrant_id(raw: str) -> str | int:
        """Qdrant acepta int o UUID. Para ids que parecen int, los pasa como int."""
        try:
            return int(raw)
        except (TypeError, ValueError):
            return raw

    # ── BaseVectorStore API ───────────────────────────────────────────────────

    async def add_documents(
        self,
        documents: List[str],
        embeddings: List[np.ndarray],
        metadatas: List[Dict[str, Any]],
        ids: List[str],
    ) -> None:
        await self._ensure_collection()

        if not (len(documents) == len(embeddings) == len(metadatas) == len(ids)):
            raise ValueError(
                "documents, embeddings, metadatas e ids deben tener el mismo largo."
            )

        points = [
            qmodels.PointStruct(
                id=self._to_qdrant_id(doc_id),
                vector=np.asarray(emb, dtype=float).tolist(),
                payload={**meta, "document": doc},
            )
            for doc, emb, meta, doc_id in zip(documents, embeddings, metadatas, ids)
        ]
        await self.client.upsert(
            collection_name=self.collection_name,
            points=points,
            wait=True,
        )

    async def query(
        self,
        query_embedding: np.ndarray,
        n_results: int = 5,
        where: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        await self._ensure_collection()

        flt = self._build_filter(where) if where else None

        # qdrant-client >= 1.10 deprecó .search() en favor de .query_points().
        # query_points() devuelve QueryResponse con .points (lista de ScoredPoint).
        response = await self.client.query_points(
            collection_name=self.collection_name,
            query=np.asarray(query_embedding, dtype=float).tolist(),
            limit=n_results,
            query_filter=flt,
            with_payload=True,
        )

        # Devolver el mismo shape que ChromaVectorStore (Dict de listas)
        # para que cualquier consumer no tenga que distinguir el backend.
        documents, metadatas, distances, ids = [], [], [], []
        for hit in response.points:
            payload = dict(hit.payload or {})
            documents.append(payload.pop("document", ""))
            metadatas.append(payload)
            # Qdrant devuelve `score`: para cosine, mayor = mejor.
            # Chroma usa `distance`: menor = mejor. Convertimos: distance = 1 - score.
            distances.append(1.0 - float(hit.score))
            ids.append(str(hit.id))

        return {
            "documents": [documents],
            "metadatas": [metadatas],
            "distances": [distances],
            "ids": [ids],
        }

    async def delete(self, ids: List[str]) -> None:
        await self._ensure_collection()
        await self.client.delete(
            collection_name=self.collection_name,
            points_selector=qmodels.PointIdsList(
                points=[self._to_qdrant_id(i) for i in ids],
            ),
            wait=True,
        )

    async def get(self, ids: List[str]) -> Dict[str, Any]:
        await self._ensure_collection()
        records = await self.client.retrieve(
            collection_name=self.collection_name,
            ids=[self._to_qdrant_id(i) for i in ids],
            with_payload=True,
        )
        documents, metadatas, out_ids = [], [], []
        for r in records:
            payload = dict(r.payload or {})
            documents.append(payload.pop("document", ""))
            metadatas.append(payload)
            out_ids.append(str(r.id))
        return {"documents": documents, "metadatas": metadatas, "ids": out_ids}

    async def count(self) -> int:
        await self._ensure_collection()
        info = await self.client.count(
            collection_name=self.collection_name,
            exact=True,
        )
        return int(info.count)

    # ── Filtros: mapear el dict tipo Chroma a Qdrant Filter ───────────────────

    @staticmethod
    def _build_filter(where: Dict[str, Any]) -> "qmodels.Filter":
        """
        Soporta:
            {"key": valor}                       igualdad exacta
            {"key": {"$eq": valor}}              igualdad explícita
            {"key": {"$in": [v1, v2]}}           cualquiera de
            {"key": {"$gte": x, "$lte": y}}      rango numérico
        """
        must: list[qmodels.FieldCondition] = []
        for key, condition in where.items():
            if not isinstance(condition, dict):
                must.append(qmodels.FieldCondition(
                    key=key, match=qmodels.MatchValue(value=condition),
                ))
                continue
            if "$eq" in condition:
                must.append(qmodels.FieldCondition(
                    key=key, match=qmodels.MatchValue(value=condition["$eq"]),
                ))
            if "$in" in condition:
                must.append(qmodels.FieldCondition(
                    key=key, match=qmodels.MatchAny(any=condition["$in"]),
                ))
            if any(k in condition for k in ("$gte", "$lte", "$gt", "$lt")):
                rng = qmodels.Range(
                    gte=condition.get("$gte"),
                    lte=condition.get("$lte"),
                    gt=condition.get("$gt"),
                    lt=condition.get("$lt"),
                )
                must.append(qmodels.FieldCondition(key=key, range=rng))
        return qmodels.Filter(must=must)

    async def close(self) -> None:
        """Cerrar conexión HTTP."""
        await self.client.close()
