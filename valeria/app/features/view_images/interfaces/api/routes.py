"""
FastAPI routes for images
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.features.view_images.interfaces.api.schemas import (
    ImageResponse,
    ImageListResponse,
    ImageCreateRequest,
    ImageUpdateRequest
)
from app.features.view_images.application.list_images_usecase import (
    ListImagesUseCase
)
from app.features.view_images.infrastructure.adapters.image_repository import (
    ImageRepository
)
from app.features.view_images.domain.image import Image
from app.infrastructure.database.session import get_db


router = APIRouter(prefix="/images", tags=["Images"])


@router.get("", response_model=ImageListResponse)
async def list_images(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    year: Optional[int] = Query(None, ge=1800, le=2100),
    location: Optional[str] = None,
    tags: Optional[List[str]] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    List images with optional filters.
    
    - **skip**: Number of images to skip (pagination)
    - **limit**: Maximum number of images to return
    - **year**: Filter by year
    - **location**: Filter by location (partial match)
    - **tags**: Filter by tags
    """
    image_repository = ImageRepository(db)
    list_images_usecase = ListImagesUseCase(image_repository)
    
    images = await list_images_usecase.execute(
        skip=skip,
        limit=limit,
        year=year,
        location=location,
        tags=tags,
        only_public=True
    )
    
    return ImageListResponse(
        total=len(images),
        skip=skip,
        limit=limit,
        images=[ImageResponse.model_validate(img) for img in images]
    )


@router.get("/{image_id}", response_model=ImageResponse)
async def get_image(
    image_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific image by ID.
    """
    image_repository = ImageRepository(db)
    image = await image_repository.get_by_id(image_id)
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image with id {image_id} not found"
        )
    
    # Check if public
    if not image.is_public:
        # TODO: Check if user has permission to view private images
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This image is not public"
        )
    
    return ImageResponse.model_validate(image)


@router.post("", response_model=ImageResponse, status_code=status.HTTP_201_CREATED)
async def create_image(
    request: ImageCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new image.
    
    Requires authentication and curator/admin role.
    """
    # TODO: Add authentication dependency
    # TODO: Check if user has curator or admin role
    
    image_repository = ImageRepository(db)
    
    image = Image(
        title=request.title,
        file_path=request.file_path,
        description=request.description,
        year=request.year,
        location=request.location,
        author=request.author,
        tags=request.tags,
        collection_id=request.collection_id,
        metadata=request.metadata,
        is_public=request.is_public
    )
    
    created_image = await image_repository.create(image)
    
    return ImageResponse.model_validate(created_image)


@router.put("/{image_id}", response_model=ImageResponse)
async def update_image(
    image_id: int,
    request: ImageUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing image.
    
    Requires authentication and curator/admin role.
    """
    # TODO: Add authentication dependency
    # TODO: Check if user has curator or admin role
    
    image_repository = ImageRepository(db)
    image = await image_repository.get_by_id(image_id)
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image with id {image_id} not found"
        )
    
    # Update fields if provided
    if request.title is not None:
        image.title = request.title
    if request.description is not None:
        image.description = request.description
    if request.year is not None:
        image.year = request.year
    if request.location is not None:
        image.location = request.location
    if request.tags is not None:
        image.tags = request.tags
    if request.is_public is not None:
        image.is_public = request.is_public
    
    updated_image = await image_repository.update(image)
    
    return ImageResponse.model_validate(updated_image)


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
    image_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an image.
    
    Requires authentication and admin role.
    """
    # TODO: Add authentication dependency
    # TODO: Check if user has admin role
    
    image_repository = ImageRepository(db)
    success = await image_repository.delete(image_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image with id {image_id} not found"
        )
    
    return None
