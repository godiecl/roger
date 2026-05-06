"""
ChromaDB vector store implementation for ROGER - Valeria API
"""

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    chromadb = None
    Settings = None

from typing import List, Dict, Optional, Any
import numpy as np

from app.infrastructure.rag.vector_stores.base_vector_store import BaseVectorStore
from app.config.settings import settings


class ChromaVectorStore(BaseVectorStore):
    """ChromaDB vector store implementation."""
    
    def __init__(self, collection_name: str = "default"):
        if not CHROMADB_AVAILABLE:
            raise ImportError(
                "ChromaDB is not installed. Install it with: pip install chromadb==0.4.22"
            )

        self.collection_name = collection_name

        # Initialize ChromaDB client
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=settings.chroma_persist_directory
        ))
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": f"Collection for {collection_name}"}
        )
    
    async def add_documents(
        self,
        documents: List[str],
        embeddings: List[np.ndarray],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ) -> None:
        """Add documents to ChromaDB."""
        # Convert numpy arrays to lists
        embeddings_list = [emb.tolist() for emb in embeddings]
        
        self.collection.add(
            documents=documents,
            embeddings=embeddings_list,
            metadatas=metadatas,
            ids=ids
        )
    
    async def query(
        self,
        query_embedding: np.ndarray,
        n_results: int = 5,
        where: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Query similar documents from ChromaDB."""
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results,
            where=where
        )
        
        return {
            'documents': results['documents'][0] if results['documents'] else [],
            'metadatas': results['metadatas'][0] if results['metadatas'] else [],
            'distances': results['distances'][0] if results['distances'] else [],
            'ids': results['ids'][0] if results['ids'] else []
        }
    
    async def delete(self, ids: List[str]) -> None:
        """Delete documents from ChromaDB."""
        self.collection.delete(ids=ids)
    
    async def get(self, ids: List[str]) -> Dict[str, Any]:
        """Get documents from ChromaDB by IDs."""
        results = self.collection.get(ids=ids)
        
        return {
            'documents': results['documents'],
            'metadatas': results['metadatas'],
            'ids': results['ids']
        }
    
    async def count(self) -> int:
        """Get total number of documents in collection."""
        return self.collection.count()


# Global vector store instances for different collections
# Only create instances if ChromaDB is available
if CHROMADB_AVAILABLE:
    image_vector_store = ChromaVectorStore("images")
    historical_vector_store = ChromaVectorStore("historical_docs")
    gazetteer_vector_store = ChromaVectorStore("gazetteer")
else:
    image_vector_store = None
    historical_vector_store = None
    gazetteer_vector_store = None
