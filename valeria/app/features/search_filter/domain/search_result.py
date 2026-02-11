"""
Search result value object
"""
from typing import List, Optional
from dataclasses import dataclass

from app.features.view_images.domain.image import Image


@dataclass
class SearchResult:
    """
    Value object representing a search result.
    Contains the matched images and relevance scores.
    """
    images: List[Image]
    total_count: int
    query: str
    relevance_scores: Optional[List[float]] = None
    search_type: str = "keyword"  # "keyword" or "semantic"
    
    def __post_init__(self):
        """Validate search result."""
        if self.total_count < 0:
            raise ValueError("total_count must be non-negative")
        
        if self.relevance_scores:
            if len(self.relevance_scores) != len(self.images):
                raise ValueError("relevance_scores length must match images length")
    
    def has_results(self) -> bool:
        """Check if there are any results."""
        return len(self.images) > 0
    
    def get_top_result(self) -> Optional[Image]:
        """Get the most relevant result."""
        if not self.images:
            return None
        return self.images[0]
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "images": [img.to_dict() for img in self.images],
            "total_count": self.total_count,
            "query": self.query,
            "relevance_scores": self.relevance_scores,
            "search_type": self.search_type
        }
