"""
Base vector store interface for ROGER - Valeria API
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
import numpy as np


class BaseVectorStore(ABC):
    """Abstract base class for vector store implementations."""
    
    @abstractmethod
    async def add_documents(
        self,
        documents: List[str],
        embeddings: List[np.ndarray],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ) -> None:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of document texts
            embeddings: List of embedding vectors
            metadatas: List of metadata dicts
            ids: List of document IDs
        """
        pass
    
    @abstractmethod
    async def query(
        self,
        query_embedding: np.ndarray,
        n_results: int = 5,
        where: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Query similar documents.
        
        Args:
            query_embedding: Query embedding vector
            n_results: Number of results to return
            where: Metadata filters
            
        Returns:
            Dict with documents, metadatas, distances, ids
        """
        pass
    
    @abstractmethod
    async def delete(self, ids: List[str]) -> None:
        """Delete documents by IDs."""
        pass
    
    @abstractmethod
    async def get(self, ids: List[str]) -> Dict[str, Any]:
        """Get documents by IDs."""
        pass
    
    @abstractmethod
    async def count(self) -> int:
        """Get total number of documents."""
        pass
