"""
SQLAlchemy Base setup for ROGER - Valeria API
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, func

# Create Base class for all models
Base = declarative_base()


class BaseModel(Base):
    """
    Abstract base model with common fields.
    All models should inherit from this.
    """
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
