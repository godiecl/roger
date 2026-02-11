"""
Pydantic schemas for search API
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from app.features.view_images.interfaces.api.schemas import ImageResponse


class SearchRequest(BaseModel):
    """Search request schema."""
    query: Optional[str] = Field(None, max_length=500, description="Search query text")
    year_from: Optional[int] = Field(None, ge=1800, le=2100, description="Start year filter")
    year_to: Optional[int] = Field(None, ge=1800, le=2100, description="End year filter")
    locations: Optional[List[str]] = Field(None, description="Location filters")
    tags: Optional[List[str]] = Field(None, description="Tag filters")
    author: Optional[str] = Field(None, max_length=255, description="Author filter")
    only_public: bool = Field(True, description="Only search public images")
    semantic_search: bool = Field(False, description="Use semantic/AI search")


class SearchResponse(BaseModel):
    """Search response schema."""
    images: List[ImageResponse]
    total_count: int
    query: str
    relevance_scores: Optional[List[float]] = None
    search_type: str  # "keyword" or "semantic"
    skip: int
    limit: int


class FacetItem(BaseModel):
    """Facet item schema."""
    value: str
    count: int


class YearFacetItem(BaseModel):
    """Year facet item schema."""
    year: int
    count: int


class LocationFacetItem(BaseModel):
    """Location facet item schema."""
    location: str
    count: int


class AuthorFacetItem(BaseModel):
    """Author facet item schema."""
    author: str
    count: int


class FacetsResponse(BaseModel):
    """Facets response schema."""
    years: List[YearFacetItem]
    locations: List[LocationFacetItem]
    authors: List[AuthorFacetItem]
    total: int
