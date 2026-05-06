"""
Search query value object
"""
from typing import Optional, List
from dataclasses import dataclass


@dataclass(frozen=True)
class SearchQuery:
    """
    Value object representing a search query.
    Immutable to ensure consistency.
    """
    query_text: Optional[str] = None
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    locations: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    author: Optional[str] = None
    only_public: bool = True
    semantic_search: bool = False
    
    def __post_init__(self):
        """Validate search query parameters."""
        if self.year_from and self.year_to:
            if self.year_from > self.year_to:
                raise ValueError("year_from must be less than or equal to year_to")
        
        if self.year_from and (self.year_from < 1800 or self.year_from > 2100):
            raise ValueError("year_from must be between 1800 and 2100")
        
        if self.year_to and (self.year_to < 1800 or self.year_to > 2100):
            raise ValueError("year_to must be between 1800 and 2100")
    
    def has_filters(self) -> bool:
        """Check if the query has any filters applied."""
        return any([
            self.query_text,
            self.year_from,
            self.year_to,
            self.locations,
            self.tags,
            self.author
        ])
    
    def is_semantic(self) -> bool:
        """Check if this is a semantic search query."""
        return self.semantic_search and bool(self.query_text)
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "query_text": self.query_text,
            "year_from": self.year_from,
            "year_to": self.year_to,
            "locations": self.locations,
            "tags": self.tags,
            "author": self.author,
            "only_public": self.only_public,
            "semantic_search": self.semantic_search
        }
