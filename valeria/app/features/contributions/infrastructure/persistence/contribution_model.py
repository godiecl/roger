"""
Metadata Contribution SQLAlchemy model for ROGER - Valeria API
User contributions to interpretive attributes (02-04, tags).
Technical Metadata (01) is excluded by business rule.
"""

from enum import Enum

from sqlalchemy import (
    Column, String, Integer, Text, DateTime,
    ForeignKey, Enum as SQLEnum,
)
from sqlalchemy.sql import func

from app.infrastructure.database.base import Base


class ContributionAttributeType(str, Enum):
    CHRONOLOGY = "chronology"
    GEOGRAPHIC = "geographic"
    ENVIRONMENTAL = "environmental"
    TAG = "tag"


class ContributionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


def _enum_values(x):
    return [e.value for e in x]


class MetadataContributionModel(Base):
    """
    Formal channel for user contributions to interpretive metadata.
    Only attributes 02-04 and tags are allowed (not TECHNICAL).
    On approval: new ACTIVE row is created in the corresponding attr_* table,
    previous ACTIVE row becomes SUPERSEDED.
    """

    __tablename__ = "metadata_contributions"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    photograph_id = Column(
        Integer, ForeignKey("photographs.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    contributor_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )
    attribute_type = Column(
        SQLEnum(ContributionAttributeType, values_callable=_enum_values),
        nullable=False, index=True,
    )
    field_name = Column(String(100), nullable=False)
    proposed_value = Column(Text, nullable=False)
    evidence_notes = Column(Text, nullable=True)
    status = Column(
        SQLEnum(ContributionStatus, values_callable=_enum_values),
        nullable=False, default=ContributionStatus.PENDING, index=True,
    )
    reviewed_by = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True,
    )
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return (
            f"<MetadataContributionModel(id={self.id}, photograph_id={self.photograph_id}, "
            f"attribute_type={self.attribute_type}, status={self.status})>"
        )
