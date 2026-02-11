"""
Use case for searching images
"""
import structlog

from app.features.search_filter.domain.search_port import SearchPort
from app.features.search_filter.domain.search_query import SearchQuery
from app.features.search_filter.domain.search_result import SearchResult

logger = structlog.get_logger()


class SearchImagesUseCase:
    """
    Use case for searching images with filters and semantic search.
    """
    
    def __init__(self, search_service: SearchPort):
        """
        Initialize the use case.
        
        Args:
            search_service: The search service adapter
        """
        self.search_service = search_service
    
    async def execute(
        self,
        query: SearchQuery,
        skip: int = 0,
        limit: int = 100
    ) -> SearchResult:
        """
        Execute the search use case.
        
        Args:
            query: The search query with filters
            skip: Number of results to skip
            limit: Maximum number of results to return
            
        Returns:
            SearchResult with matched images
        """
        logger.info(
            "Executing search",
            query_text=query.query_text,
            semantic=query.is_semantic(),
            has_filters=query.has_filters()
        )
        
        # Decide between semantic and keyword search
        if query.is_semantic():
            logger.info("Performing semantic search", query=query.query_text)
            return await self.search_service.semantic_search(
                query_text=query.query_text,
                limit=limit,
                only_public=query.only_public
            )
        else:
            logger.info("Performing filtered search")
            return await self.search_service.search(
                query=query,
                skip=skip,
                limit=limit
            )
    
    async def get_search_facets(self, query: SearchQuery) -> dict:
        """
        Get faceted search results for the query.
        
        Args:
            query: The search query
            
        Returns:
            Dictionary with facet counts
        """
        logger.info("Getting search facets")
        return await self.search_service.get_facets(query)
