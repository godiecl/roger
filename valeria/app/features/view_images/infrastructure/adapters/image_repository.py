"""
Image repository implementation for ROGER - Valeria API
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_

from app.features.view_images.domain.image import Image
from app.features.view_images.domain.image_port import IImageRepository
from app.features.view_images.infrastructure.persistence.image_model import ImageModel


class ImageRepository(IImageRepository):
    """SQLAlchemy implementation of image repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, image: Image) -> Image:
        """Create a new image."""
        image_model = ImageModel(
            title=image.title,
            file_path=image.file_path,
            description=image.description,
            year=image.year,
            location=image.location,
            author=image.author,
            tags=image.tags,
            collection_id=image.collection_id,
            image_metadata=image.metadata,
            is_public=image.is_public
        )
        
        self.session.add(image_model)
        await self.session.flush()
        await self.session.refresh(image_model)
        
        return self._to_entity(image_model)
    
    async def get_by_id(self, image_id: int) -> Optional[Image]:
        """Get image by ID."""
        result = await self.session.execute(
            select(ImageModel).where(ImageModel.id == image_id)
        )
        image_model = result.scalar_one_or_none()
        
        return self._to_entity(image_model) if image_model else None
    
    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        only_public: bool = True
    ) -> List[Image]:
        """List all images with pagination."""
        query = select(ImageModel)
        
        if only_public:
            query = query.where(ImageModel.is_public == True)
        
        query = query.offset(skip).limit(limit).order_by(ImageModel.created_at.desc())
        
        result = await self.session.execute(query)
        image_models = result.scalars().all()
        
        return [self._to_entity(model) for model in image_models]
    
    async def filter_by_year(self, year: int) -> List[Image]:
        """Filter images by year."""
        result = await self.session.execute(
            select(ImageModel).where(ImageModel.year == year)
        )
        image_models = result.scalars().all()
        
        return [self._to_entity(model) for model in image_models]
    
    async def filter_by_location(self, location: str) -> List[Image]:
        """Filter images by location."""
        result = await self.session.execute(
            select(ImageModel).where(ImageModel.location.ilike(f"%{location}%"))
        )
        image_models = result.scalars().all()
        
        return [self._to_entity(model) for model in image_models]
    
    async def filter_by_tags(self, tags: List[str]) -> List[Image]:
        """Filter images by tags."""
        # Note: This is a simple implementation
        # For production, you might want a more sophisticated tag search
        result = await self.session.execute(
            select(ImageModel)
        )
        all_images = result.scalars().all()
        
        # Filter images that have at least one of the specified tags
        filtered = [
            model for model in all_images
            if any(tag in model.tags for tag in tags)
        ]
        
        return [self._to_entity(model) for model in filtered]
    
    async def update(self, image: Image) -> Image:
        """Update an existing image."""
        result = await self.session.execute(
            select(ImageModel).where(ImageModel.id == image.id)
        )
        image_model = result.scalar_one_or_none()
        
        if not image_model:
            raise ValueError(f"Image with id {image.id} not found")
        
        image_model.title = image.title
        image_model.file_path = image.file_path
        image_model.description = image.description
        image_model.year = image.year
        image_model.location = image.location
        image_model.author = image.author
        image_model.tags = image.tags
        image_model.collection_id = image.collection_id
        image_model.image_metadata = image.metadata
        image_model.is_public = image.is_public
        
        await self.session.flush()
        await self.session.refresh(image_model)
        
        return self._to_entity(image_model)
    
    async def delete(self, image_id: int) -> bool:
        """Delete an image."""
        result = await self.session.execute(
            select(ImageModel).where(ImageModel.id == image_id)
        )
        image_model = result.scalar_one_or_none()
        
        if image_model:
            await self.session.delete(image_model)
            return True
        return False
    
    def _to_entity(self, model: ImageModel) -> Image:
        """Convert SQLAlchemy model to domain entity."""
        return Image(
            id=model.id,
            title=model.title,
            file_path=model.file_path,
            description=model.description,
            year=model.year,
            location=model.location,
            author=model.author,
            tags=model.tags if model.tags else [],
            collection_id=model.collection_id,
            metadata=model.image_metadata if model.image_metadata else {},
            is_public=model.is_public,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
