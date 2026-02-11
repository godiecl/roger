"""
Base retriever interface for ROGER - Valeria API
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseRetriever(ABC):
    """Abstract base class for retriever implementations."""
    
    @abstractmethod
    async def retrieve(
        self,
        query: str,
        n_results: int = 10,
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Query string
            n_results: Number of results to return
            filters: Optional metadata filters
            
        Returns:
            List of documents with metadata and scores
        """
        pass
