"""
Base knowledge base interface for ROGER - Valeria API
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseKnowledgeBase(ABC):
    """Abstract base class for knowledge base implementations."""
    
    @abstractmethod
    async def add_document(self, document: Dict[str, Any]) -> str:
        """
        Add a document to the knowledge base.
        
        Args:
            document: Document dict with 'text' and 'metadata'
            
        Returns:
            Document ID
        """
        pass
    
    @abstractmethod
    async def search(
        self,
        query: str,
        n_results: int = 5,
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Search the knowledge base.
        
        Args:
            query: Search query
            n_results: Number of results
            filters: Metadata filters
            
        Returns:
            List of matching documents
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, doc_id: str) -> Dict[str, Any]:
        """Get a document by ID."""
        pass
    
    @abstractmethod
    async def delete(self, doc_id: str) -> bool:
        """Delete a document."""
        pass
