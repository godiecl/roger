"""
FastAPI routes for search
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.features.search_filter.interfaces.api.schemas import (
    SearchRequest,
    SearchResponse,
    FacetsResponse,
    YearFacetItem,
    LocationFacetItem,
    AuthorFacetItem
)
from app.features.search_filter.application.search_images_usecase import (
    SearchImagesUseCase
)
from app.features.search_filter.infrastructure.adapters.search_service import (
    SearchService
)
from app.features.search_filter.domain.search_query import SearchQuery
from app.features.view_images.interfaces.api.schemas import ImageResponse
from app.infrastructure.database.session import get_db
from app.infrastructure.rag.vector_stores.chroma_store import ChromaVectorStore
from app.config.settings import settings


router = APIRouter(prefix="/search", tags=["Search"])


def get_chroma_store() -> ChromaVectorStore:
    """Get ChromaDB vector store instance."""
    try:
        return ChromaVectorStore(persist_directory=settings.chroma_persist_directory)
    except Exception:
        # If ChromaDB is not available, return None
        return None


@router.get("", response_model=SearchResponse)
async def search_images(
    query: Optional[str] = Query(None, max_length=500),
    year_from: Optional[int] = Query(None, ge=1800, le=2100),
    year_to: Optional[int] = Query(None, ge=1800, le=2100),
    locations: Optional[List[str]] = Query(None),
    tags: Optional[List[str]] = Query(None),
    author: Optional[str] = Query(None, max_length=255),
    only_public: bool = Query(True),
    semantic: bool = Query(False, description="Enable semantic/AI search"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """
    Search images with various filters.

    - **query**: Text to search in title, description, and location
    - **year_from**: Filter images from this year onwards
    - **year_to**: Filter images up to this year
    - **locations**: Filter by specific locations (can specify multiple)
    - **tags**: Filter by tags (can specify multiple)
    - **author**: Filter by author name
    - **only_public**: Only search public images (default: true)
    - **semantic**: Use AI-powered semantic search (requires OpenAI API key)
    - **skip**: Number of results to skip (pagination)
    - **limit**: Maximum number of results to return
    """
    # Create search query
    search_query = SearchQuery(
        query_text=query,
        year_from=year_from,
        year_to=year_to,
        locations=locations,
        tags=tags,
        author=author,
        only_public=only_public,
        semantic_search=semantic
    )

    # Initialize search service
    vector_store = get_chroma_store() if semantic else None
    search_service = SearchService(db, vector_store)
    search_usecase = SearchImagesUseCase(search_service)

    # Execute search
    result = await search_usecase.execute(
        query=search_query,
        skip=skip,
        limit=limit
    )

    return SearchResponse(
        images=[ImageResponse.model_validate(img) for img in result.images],
        total_count=result.total_count,
        query=result.query,
        relevance_scores=result.relevance_scores,
        search_type=result.search_type,
        skip=skip,
        limit=limit
    )


@router.get("/facets", response_model=FacetsResponse)
async def get_search_facets(
    only_public: bool = Query(True),
    db: AsyncSession = Depends(get_db)
):
    """
    Get faceted search results (aggregations by year, location, author).

    Useful for building filter interfaces in the frontend.

    - **only_public**: Only include public images in facets
    """
    # Create base query
    search_query = SearchQuery(only_public=only_public)

    # Initialize search service
    search_service = SearchService(db)
    search_usecase = SearchImagesUseCase(search_service)

    # Get facets
    facets = await search_usecase.get_search_facets(search_query)

    return FacetsResponse(
        years=[
            YearFacetItem(year=item["year"], count=item["count"])
            for item in facets.get("years", [])
        ],
        locations=[
            LocationFacetItem(location=item["location"], count=item["count"])
            for item in facets.get("locations", [])
        ],
        authors=[
            AuthorFacetItem(author=item["author"], count=item["count"])
            for item in facets.get("authors", [])
        ],
        total=facets.get("total", 0)
    )


@router.post("", response_model=SearchResponse)
async def search_images_post(
    request: SearchRequest,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """
    Search images using POST method (for complex queries).

    Same as GET /search but accepts a JSON body instead of query parameters.
    Useful when you have many filters or long query text.
    """
    # Create search query
    search_query = SearchQuery(
        query_text=request.query,
        year_from=request.year_from,
        year_to=request.year_to,
        locations=request.locations,
        tags=request.tags,
        author=request.author,
        only_public=request.only_public,
        semantic_search=request.semantic_search
    )

    # Initialize search service
    vector_store = get_chroma_store() if request.semantic_search else None
    search_service = SearchService(db, vector_store)
    search_usecase = SearchImagesUseCase(search_service)

    # Execute search
    result = await search_usecase.execute(
        query=search_query,
        skip=skip,
        limit=limit
    )

    return SearchResponse(
        images=[ImageResponse.model_validate(img) for img in result.images],
        total_count=result.total_count,
        query=result.query,
        relevance_scores=result.relevance_scores,
        search_type=result.search_type,
        skip=skip,
        limit=limit
    )
