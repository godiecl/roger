"""
Tag SQLAlchemy models for ROGER - Valeria API
Tags and PhotographTags with full source traceability
"""

from enum import Enum

from sqlalchemy import (
    Column, String, Integer, Float, DateTime,
    ForeignKey, Enum as SQLEnum, UniqueConstraint,
)
from sqlalchemy.sql import func

from app.infrastructure.database.base import Base


class TagCategory(str, Enum):
    GEOGRAPHIC = "geographic"
    TEMPORAL = "temporal"
    ICONOGRAPHIC = "iconographic"
    TECHNICAL = "technical"
    AI_INFERRED = "ai_inferred"


class TagSource(str, Enum):
    MANUAL = "manual"
    AI = "ai"
    USER_CONTRIBUTED = "user_contributed"
    METADATA = "metadata"


class TagStatus(str, Enum):
    APPROVED = "approved"
    PENDING = "pending"
    REJECTED = "rejected"


def _enum_values(x):
    return [e.value for e in x]


class TagModel(Base):
    """Controlled vocabulary tag, global or collection-specific."""

    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    category = Column(
        SQLEnum(TagCategory, values_callable=_enum_values),
        nullable=False,
    )
    collection_id = Column(
        Integer, ForeignKey("collections.id", ondelete="CASCADE"),
        nullable=True, index=True,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("name", "collection_id", name="uq_tag_name_collection"),
    )

    def __repr__(self) -> str:
        return f"<TagModel(id={self.id}, name={self.name}, category={self.category})>"


class PhotographTagModel(Base):
    """
    Photograph-Tag relationship with full traceability.
    AI tags and user contributions start as PENDING until curator approves.
    originated_from_attribute: which taxonomy attribute (1-9) generated this tag.
    """

    __tablename__ = "photograph_tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    photograph_id = Column(
        Integer, ForeignKey("photographs.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    tag_id = Column(
        Integer, ForeignKey("tags.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    source = Column(
        SQLEnum(TagSource, values_callable=_enum_values),
        nullable=False,
    )
    confidence = Column(Float, nullable=True)
    status = Column(
        SQLEnum(TagStatus, values_callable=_enum_values),
        nullable=False, default=TagStatus.PENDING, index=True,
    )
    originated_from_attribute = Column(Integer, nullable=True)
    approved_by = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True,
    )
    approved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("photograph_id", "tag_id", "source", name="uq_photograph_tag_source"),
    )

    def __repr__(self) -> str:
        return f"<PhotographTagModel(photograph_id={self.photograph_id}, tag_id={self.tag_id}, status={self.status})>"
