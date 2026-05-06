"""
Vector store factory for ROGER - Valeria API
"""

from typing import Optional
from app.infrastructure.rag.vector_stores.base_vector_store import BaseVectorStore
from app.infrastructure.rag.vector_stores.chroma_store import ChromaVectorStore


class VectorStoreFactory:
    """Factory for creating vector store instances."""
    
    @staticmethod
    def create(
        store_type: str = "chroma",
        collection_name: str = "default"
    ) -> BaseVectorStore:
        """
        Create a vector store instance.
        
        Args:
            store_type: Type of vector store ("chroma", "qdrant", etc.)
            collection_name: Name of the collection
            
        Returns:
            Vector store instance
        """
        if store_type == "chroma":
            return ChromaVectorStore(collection_name)
        # Add more implementations here (Qdrant, Weaviate, etc.)
        else:
            raise ValueError(f"Unknown vector store type: {store_type}")


# Convenience function
def get_vector_store(collection_name: str = "default") -> BaseVectorStore:
    """Get a vector store instance for a collection."""
    return VectorStoreFactory.create("chroma", collection_name)
