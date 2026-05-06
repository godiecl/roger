"""
Port interface for search operations
"""
from abc import ABC, abstractmethod
from typing import List

from app.features.search_filter.domain.search_query import SearchQuery
from app.features.search_filter.domain.search_result import SearchResult


class SearchPort(ABC):
    """
    Port interface for search operations.
    Defines the contract that adapters must implement.
    """
    
    @abstractmethod
    async def search(
        self,
        query: SearchQuery,
        skip: int = 0,
        limit: int = 100
    ) -> SearchResult:
        """
        Perform a search based on the given query.
        
        Args:
            query: The search query with filters
            skip: Number of results to skip
            limit: Maximum number of results to return
            
        Returns:
            SearchResult with matched images
        """
        pass
    
    @abstractmethod
    async def semantic_search(
        self,
        query_text: str,
        limit: int = 10,
        only_public: bool = True
    ) -> SearchResult:
        """
        Perform semantic search using embeddings and vector similarity.
        
        Args:
            query_text: Natural language query
            limit: Maximum number of results
            only_public: Only search public images
            
        Returns:
            SearchResult with semantically similar images
        """
        pass
    
    @abstractmethod
    async def get_facets(self, query: SearchQuery) -> dict:
        """
        Get faceted search results (aggregations).
        
        Args:
            query: The search query
            
        Returns:
            Dictionary with facet counts (years, locations, tags, etc.)
        """
        pass
