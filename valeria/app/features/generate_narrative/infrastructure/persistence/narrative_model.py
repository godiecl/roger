"""
SQLAlchemy model for narratives
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from app.infrastructure.database.base import Base


class NarrativeModel(Base):
    """
    SQLAlchemy model for narratives table.
    """
    __tablename__ = "narratives"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id", ondelete="CASCADE"), nullable=False, index=True)
    text = Column(Text, nullable=False)

    # Trazabilidad (stored as JSON)
    trazabilidad = Column(JSON, nullable=False)

    # Generation metadata
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    prompt = Column(Text, nullable=True)
    language = Column(String(10), nullable=False, default="es", index=True)
    model_used = Column(String(100), nullable=True)
    generation_time_ms = Column(Integer, nullable=True)

    # Approval workflow
    is_approved = Column(Boolean, default=False, nullable=False, index=True)
    approved_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    # image = relationship("ImageModel", back_populates="narratives")
    # user = relationship("UserModel", foreign_keys=[user_id])
    # approver = relationship("UserModel", foreign_keys=[approved_by])

    def __repr__(self):
        return f"<NarrativeModel(id={self.id}, image_id={self.image_id}, language={self.language})>"
