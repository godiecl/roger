"""
List images use case for ROGER - Valeria API
"""

from typing import List, Optional

from app.features.view_images.domain.image import Image
from app.features.view_images.domain.image_port import IImageRepository


class ListImagesUseCase:
    """
    Use case for listing images with optional filters.
    """
    
    def __init__(self, image_repository: IImageRepository):
        self.image_repository = image_repository
    
    async def execute(
        self,
        skip: int = 0,
        limit: int = 100,
        year: Optional[int] = None,
        location: Optional[str] = None,
        tags: Optional[List[str]] = None,
        only_public: bool = True
    ) -> List[Image]:
        """
        List images with optional filters.
        
        Args:
            skip: Number of images to skip (pagination)
            limit: Maximum number of images to return
            year: Filter by year
            location: Filter by location
            tags: Filter by tags
            only_public: Only return public images
            
        Returns:
            List of images
        """
        # Apply filters
        if year:
            images = await self.image_repository.filter_by_year(year)
        elif location:
            images = await self.image_repository.filter_by_location(location)
        elif tags:
            images = await self.image_repository.filter_by_tags(tags)
        else:
            images = await self.image_repository.list_all(
                skip=skip,
                limit=limit,
                only_public=only_public
            )
        
        return images
