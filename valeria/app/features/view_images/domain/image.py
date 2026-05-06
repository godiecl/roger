"""
Image entity for ROGER - Valeria API
"""

from datetime import datetime
from typing import Optional, List

from app.shared.domain.base_entity import BaseEntity


class Image(BaseEntity):
    """
    Image domain entity.
    Represents a historical photograph in the Gerstmann collection.
    """
    
    def __init__(
        self,
        title: str,
        file_path: str,
        description: Optional[str] = None,
        year: Optional[int] = None,
        location: Optional[str] = None,
        author: str = "Robert Gerstmann",
        tags: Optional[List[str]] = None,
        collection_id: Optional[int] = None,
        metadata: Optional[dict] = None,
        is_public: bool = True,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        super().__init__(id, created_at, updated_at)
        self.title = title
        self.file_path = file_path
        self.description = description
        self.year = year
        self.location = location
        self.author = author
        self.tags = tags or []
        self.collection_id = collection_id
        self.metadata = metadata or {}
        self.is_public = is_public
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the image."""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.utcnow()
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the image."""
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.utcnow()
    
    def update_description(self, description: str) -> None:
        """Update image description."""
        self.description = description
        self.updated_at = datetime.utcnow()
    
    def make_public(self) -> None:
        """Make image publicly visible."""
        self.is_public = True
        self.updated_at = datetime.utcnow()
    
    def make_private(self) -> None:
        """Make image private."""
        self.is_public = False
        self.updated_at = datetime.utcnow()
    
    def __repr__(self) -> str:
        return f"Image(id={self.id}, title={self.title}, year={self.year})"
