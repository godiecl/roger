"""
Vector store factory for ROGER - Valeria API.

El proveedor se decide en este orden:
  1. Parámetro `store_type` si se pasa explícito (tests, scripts puntuales).
  2. settings.vector_store_provider — leído del env VECTOR_STORE_PROVIDER.
  3. "chroma" como default histórico para dev/MVP.

Adapters disponibles:
  - chroma  → ChromaVectorStore  (dev/MVP, embebido, persistencia en disco)
  - qdrant  → QdrantVectorStore  (prod, server externo, ver docker-compose.prod.yml)
"""
from typing import Optional

from app.config.settings import settings
from app.infrastructure.rag.vector_stores.base_vector_store import BaseVectorStore
from app.infrastructure.rag.vector_stores.chroma_store import ChromaVectorStore
from app.infrastructure.rag.vector_stores.qdrant_store import QdrantVectorStore


class VectorStoreFactory:
    """Factory for creating vector store instances."""

    @staticmethod
    def create(
        store_type: Optional[str] = None,
        collection_name: str = "default",
    ) -> BaseVectorStore:
        """
        Create a vector store instance.

        Args:
            store_type: Override explícito ("chroma" | "qdrant"). Si None, se
                lee settings.vector_store_provider.
            collection_name: Name of the collection.

        Returns:
            Vector store instance.
        """
        provider = (store_type or settings.vector_store_provider or "chroma").lower()

        if provider == "qdrant":
            return QdrantVectorStore(collection_name)
        if provider == "chroma":
            return ChromaVectorStore(collection_name)
        raise ValueError(f"Unknown vector store provider: {provider}")


def get_vector_store(collection_name: str = "default") -> BaseVectorStore:
    """Get a vector store instance using the configured provider."""
    return VectorStoreFactory.create(collection_name=collection_name)
