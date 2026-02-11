"""
Image and Collection SQLAlchemy models for ROGER - Valeria API
"""

from sqlalchemy import Column, String, Integer, Boolean, JSON, Text, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY

from app.infrastructure.database.base import BaseModel


class ImageModel(BaseModel):
    """SQLAlchemy model for Image table."""
    
    __tablename__ = "images"
    
    title = Column(String(255), nullable=False, index=True)
    file_path = Column(String(512), nullable=False)
    description = Column(Text, nullable=True)
    year = Column(Integer, nullable=True, index=True)
    location = Column(String(255), nullable=True, index=True)
    author = Column(String(255), nullable=False, default="Robert Gerstmann")
    tags = Column(JSON, nullable=True, default=list)  # Stored as JSON array
    collection_id = Column(Integer, ForeignKey("collections.id"), nullable=True)
    image_metadata = Column(JSON, nullable=True, default=dict)  # Renamed from 'metadata' (reserved word)
    is_public = Column(Boolean, default=True, nullable=False, index=True)
    
    def __repr__(self) -> str:
        return f"<ImageModel(id={self.id}, title={self.title}, year={self.year})>"


class CollectionModel(BaseModel):
    """SQLAlchemy model for Collection table."""

    __tablename__ = "collections"

    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    def __repr__(self) -> str:
        return f"<CollectionModel(id={self.id}, name={self.name})>"
