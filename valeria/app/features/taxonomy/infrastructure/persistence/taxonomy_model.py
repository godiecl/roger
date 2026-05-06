"""
Taxonomy SQLAlchemy models for ROGER - Valeria API
Attributes 01-04: TechnicalMetadata, ChronologyDating, GeographicReference, EnvironmentalSpatial
"""

from enum import Enum

from sqlalchemy import (
    Column, String, Integer, Boolean, Text, Date, Float, JSON,
    ForeignKey, Enum as SQLEnum, DateTime,
)
from sqlalchemy.sql import func

from app.infrastructure.database.base import Base


class AttributeStatus(str, Enum):
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    PENDING = "pending"


class SourceType(str, Enum):
    AI = "ai"
    CURATOR = "curator"
    USER_APPROVED = "user_approved"


class DateType(str, Enum):
    PRECISE = "precise"
    APPROXIMATE = "approximate"
    RANGE = "range"
    UNKNOWN = "unknown"


class LocationType(str, Enum):
    PRECISE = "precise"
    APPROXIMATE = "approximate"
    UNKNOWN = "unknown"


class SettingType(str, Enum):
    NATURAL = "natural"
    URBAN = "urban"
    INTERIOR = "interior"
    EXTERIOR = "exterior"
    MIXED = "mixed"


class ConservationState(str, Enum):
    PRISTINE = "pristine"
    BUILT = "built"
    ANTHROPOGENIC = "anthropogenic"


def _enum_values(x):
    return [e.value for e in x]


class AttrTechnicalMetadataModel(Base):
    """
    Attribute 01 — Technical Metadata.
    IMMUTABLE: written only by authorized analysis tools, never by user contributions.
    Multiple rows per photograph preserved for full audit trail.
    """

    __tablename__ = "attr_technical_metadata"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    photograph_id = Column(
        Integer, ForeignKey("photographs.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    status = Column(
        SQLEnum(AttributeStatus, values_callable=_enum_values),
        nullable=False, default=AttributeStatus.ACTIVE, index=True,
    )
    # Basic level
    film_format = Column(String(50), nullable=True)
    manufacturer = Column(String(100), nullable=True)
    emulsion_type = Column(String(100), nullable=True)
    iso_sensitivity = Column(String(20), nullable=True)
    mounting_marks = Column(String(255), nullable=True)
    scanning_artifacts = Column(String(255), nullable=True)
    physical_status = Column(String(20), nullable=True)
    # Advanced level
    exposure = Column(String(50), nullable=True)
    diaphragm_aperture = Column(String(50), nullable=True)
    lens_optical = Column(String(100), nullable=True)
    camera_settings = Column(String(255), nullable=True)
    deterioration_notes = Column(Text, nullable=True)
    digitizer_person = Column(String(255), nullable=True)
    is_estimated = Column(Boolean, default=False, nullable=False)
    # Traceability
    analysis_provider = Column(String(100), nullable=True)
    provider_version = Column(String(50), nullable=True)
    confidence_level = Column(Float, nullable=True)
    raw_output = Column(JSON, nullable=True)
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<AttrTechnicalMetadataModel(id={self.id}, photograph_id={self.photograph_id}, status={self.status})>"


class AttrChronologyDatingModel(Base):
    """
    Attribute 02 — Chronology & Dating.
    Accepts curator edits and approved user contributions.
    Multiple rows per photograph (ACTIVE/SUPERSEDED/PENDING).
    """

    __tablename__ = "attr_chronology_dating"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    photograph_id = Column(
        Integer, ForeignKey("photographs.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    status = Column(
        SQLEnum(AttributeStatus, values_callable=_enum_values),
        nullable=False, default=AttributeStatus.PENDING, index=True,
    )
    source_type = Column(
        SQLEnum(SourceType, values_callable=_enum_values),
        nullable=False, default=SourceType.AI,
    )
    date_type = Column(
        SQLEnum(DateType, values_callable=_enum_values),
        nullable=True,
    )
    precise_date = Column(Date, nullable=True)
    date_from = Column(Date, nullable=True)
    date_to = Column(Date, nullable=True)
    date_hypothesis = Column(Text, nullable=True)
    verification_source = Column(String(255), nullable=True)
    methodology = Column(Text, nullable=True)
    visual_evidence_notes = Column(Text, nullable=True)
    # Traceability
    analysis_provider = Column(String(100), nullable=True)
    provider_version = Column(String(50), nullable=True)
    confidence_level = Column(Float, nullable=True)
    raw_output = Column(JSON, nullable=True)
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<AttrChronologyDatingModel(id={self.id}, photograph_id={self.photograph_id}, status={self.status})>"


class AttrGeographicReferenceModel(Base):
    """
    Attribute 03 — Geographic Reference.
    Accepts curator edits and approved user contributions.
    Multiple rows per photograph (ACTIVE/SUPERSEDED/PENDING).
    """

    __tablename__ = "attr_geographic_reference"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    photograph_id = Column(
        Integer, ForeignKey("photographs.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    status = Column(
        SQLEnum(AttributeStatus, values_callable=_enum_values),
        nullable=False, default=AttributeStatus.PENDING, index=True,
    )
    source_type = Column(
        SQLEnum(SourceType, values_callable=_enum_values),
        nullable=False, default=SourceType.AI,
    )
    location_type = Column(
        SQLEnum(LocationType, values_callable=_enum_values),
        nullable=True,
    )
    geographic_location = Column(String(512), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    location_radius_km = Column(Float, nullable=True)
    signage_found = Column(Text, nullable=True)
    architectural_landmarks = Column(Text, nullable=True)
    landscape_features = Column(Text, nullable=True)
    # Traceability
    analysis_provider = Column(String(100), nullable=True)
    provider_version = Column(String(50), nullable=True)
    confidence_level = Column(Float, nullable=True)
    raw_output = Column(JSON, nullable=True)
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<AttrGeographicReferenceModel(id={self.id}, photograph_id={self.photograph_id}, status={self.status})>"


class AttrEnvironmentalSpatialModel(Base):
    """
    Attribute 04 — Environmental & Spatial Context.
    Accepts curator edits and approved user contributions.
    Multiple rows per photograph (ACTIVE/SUPERSEDED/PENDING).
    """

    __tablename__ = "attr_environmental_spatial"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    photograph_id = Column(
        Integer, ForeignKey("photographs.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    status = Column(
        SQLEnum(AttributeStatus, values_callable=_enum_values),
        nullable=False, default=AttributeStatus.PENDING, index=True,
    )
    source_type = Column(
        SQLEnum(SourceType, values_callable=_enum_values),
        nullable=False, default=SourceType.AI,
    )
    setting_type = Column(
        SQLEnum(SettingType, values_callable=_enum_values),
        nullable=True,
    )
    specific_typology = Column(String(255), nullable=True)
    conservation_state = Column(
        SQLEnum(ConservationState, values_callable=_enum_values),
        nullable=True,
    )
    human_env_relationship = Column(Text, nullable=True)
    # Traceability
    analysis_provider = Column(String(100), nullable=True)
    provider_version = Column(String(50), nullable=True)
    confidence_level = Column(Float, nullable=True)
    raw_output = Column(JSON, nullable=True)
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<AttrEnvironmentalSpatialModel(id={self.id}, photograph_id={self.photograph_id}, status={self.status})>"
