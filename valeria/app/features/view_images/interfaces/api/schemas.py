"""
Pydantic schemas for images API
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class ImageResponse(BaseModel):
    """Image response schema."""
    id: int
    title: str
    file_path: str
    description: Optional[str]
    year: Optional[int]
    location: Optional[str]
    author: str
    tags: List[str] = []
    collection_id: Optional[int]
    metadata: Dict = {}
    is_public: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ImageListResponse(BaseModel):
    """Image list response schema."""
    total: int
    skip: int
    limit: int
    images: List[ImageResponse]


class ImageCreateRequest(BaseModel):
    """Image create request schema."""
    title: str = Field(..., min_length=1, max_length=255)
    file_path: str = Field(..., min_length=1)
    description: Optional[str] = None
    year: Optional[int] = Field(None, ge=1800, le=2100)
    location: Optional[str] = None
    author: str = "Robert Gerstmann"
    tags: List[str] = []
    collection_id: Optional[int] = None
    metadata: Dict = {}
    is_public: bool = True


class ImageUpdateRequest(BaseModel):
    """Image update request schema."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    year: Optional[int] = Field(None, ge=1800, le=2100)
    location: Optional[str] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None
