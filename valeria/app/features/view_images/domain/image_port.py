"""
Image repository port (interface) for ROGER - Valeria API
"""

from abc import ABC, abstractmethod
from typing import Optional, List

from app.features.view_images.domain.image import Image


class IImageRepository(ABC):
    """Repository interface for Image aggregate."""
    
    @abstractmethod
    async def create(self, image: Image) -> Image:
        """Create a new image."""
        pass
    
    @abstractmethod
    async def get_by_id(self, image_id: int) -> Optional[Image]:
        """Get image by ID."""
        pass
    
    @abstractmethod
    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        only_public: bool = True
    ) -> List[Image]:
        """List all images with pagination."""
        pass
    
    @abstractmethod
    async def filter_by_year(self, year: int) -> List[Image]:
        """Filter images by year."""
        pass
    
    @abstractmethod
    async def filter_by_location(self, location: str) -> List[Image]:
        """Filter images by location."""
        pass
    
    @abstractmethod
    async def filter_by_tags(self, tags: List[str]) -> List[Image]:
        """Filter images by tags."""
        pass
    
    @abstractmethod
    async def update(self, image: Image) -> Image:
        """Update an existing image."""
        pass
    
    @abstractmethod
    async def delete(self, image_id: int) -> bool:
        """Delete an image."""
        pass
