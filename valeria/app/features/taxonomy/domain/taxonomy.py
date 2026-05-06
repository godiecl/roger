"""
Taxonomy domain entities for ROGER - Valeria API.
Attributes 01-04: TechnicalMetadata, ChronologyDating, GeographicReference, EnvironmentalSpatial.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional


class AttributeStatus(str, Enum):
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    PENDING = "pending"


class SourceType(str, Enum):
    AI = "ai"
    CURATOR = "curator"
    USER_APPROVED = "user_approved"


class TechnicalMetadata:
    """
    Domain entity for Attribute 01 — Technical Metadata.
    Immutable: created only by analysis tools, never by user contribution.
    """

    def __init__(
        self,
        photograph_id: int,
        status: AttributeStatus = AttributeStatus.ACTIVE,
        film_format: Optional[str] = None,
        manufacturer: Optional[str] = None,
        emulsion_type: Optional[str] = None,
        iso_sensitivity: Optional[str] = None,
        mounting_marks: Optional[str] = None,
        scanning_artifacts: Optional[str] = None,
        physical_status: Optional[str] = None,
        exposure: Optional[str] = None,
        diaphragm_aperture: Optional[str] = None,
        lens_optical: Optional[str] = None,
        camera_settings: Optional[str] = None,
        deterioration_notes: Optional[str] = None,
        digitizer_person: Optional[str] = None,
        is_estimated: bool = False,
        analysis_provider: Optional[str] = None,
        provider_version: Optional[str] = None,
        confidence_level: Optional[float] = None,
        raw_output: Optional[Any] = None,
        analyzed_at: Optional[datetime] = None,
        id: Optional[int] = None,
    ):
        self.id = id
        self.photograph_id = photograph_id
        self.status = status
        self.film_format = film_format
        self.manufacturer = manufacturer
        self.emulsion_type = emulsion_type
        self.iso_sensitivity = iso_sensitivity
        self.mounting_marks = mounting_marks
        self.scanning_artifacts = scanning_artifacts
        self.physical_status = physical_status
        self.exposure = exposure
        self.diaphragm_aperture = diaphragm_aperture
        self.lens_optical = lens_optical
        self.camera_settings = camera_settings
        self.deterioration_notes = deterioration_notes
        self.digitizer_person = digitizer_person
        self.is_estimated = is_estimated
        self.analysis_provider = analysis_provider
        self.provider_version = provider_version
        self.confidence_level = confidence_level
        self.raw_output = raw_output
        self.analyzed_at = analyzed_at or datetime.utcnow()

    def __repr__(self) -> str:
        return f"TechnicalMetadata(id={self.id}, photograph_id={self.photograph_id}, status={self.status})"


class ChronologyDating:
    """
    Domain entity for Attribute 02 — Chronological Dating.
    Accepts AI-generated and curator/user-contributed records.
    """

    def __init__(
        self,
        photograph_id: int,
        status: AttributeStatus = AttributeStatus.ACTIVE,
        source_type: SourceType = SourceType.AI,
        date_type: Optional[str] = None,
        precise_date: Optional[Any] = None,
        date_from: Optional[Any] = None,
        date_to: Optional[Any] = None,
        date_hypothesis: Optional[str] = None,
        verification_source: Optional[str] = None,
        methodology: Optional[str] = None,
        visual_evidence_notes: Optional[str] = None,
        analysis_provider: Optional[str] = None,
        provider_version: Optional[str] = None,
        confidence_level: Optional[float] = None,
        raw_output: Optional[Any] = None,
        analyzed_at: Optional[datetime] = None,
        id: Optional[int] = None,
    ):
        self.id = id
        self.photograph_id = photograph_id
        self.status = status
        self.source_type = source_type
        self.date_type = date_type
        self.precise_date = precise_date
        self.date_from = date_from
        self.date_to = date_to
        self.date_hypothesis = date_hypothesis
        self.verification_source = verification_source
        self.methodology = methodology
        self.visual_evidence_notes = visual_evidence_notes
        self.analysis_provider = analysis_provider
        self.provider_version = provider_version
        self.confidence_level = confidence_level
        self.raw_output = raw_output
        self.analyzed_at = analyzed_at or datetime.utcnow()

    def __repr__(self) -> str:
        return (
            f"ChronologyDating(id={self.id}, photograph_id={self.photograph_id}, "
            f"status={self.status}, date_type={self.date_type})"
        )


class GeographicReference:
    """
    Domain entity for Attribute 03 — Geographic Reference.
    Accepts AI-generated and curator/user-contributed records.
    """

    def __init__(
        self,
        photograph_id: int,
        status: AttributeStatus = AttributeStatus.ACTIVE,
        source_type: SourceType = SourceType.AI,
        location_type: Optional[str] = None,
        geographic_location: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        location_radius_km: Optional[float] = None,
        signage_found: Optional[str] = None,
        architectural_landmarks: Optional[str] = None,
        landscape_features: Optional[str] = None,
        analysis_provider: Optional[str] = None,
        provider_version: Optional[str] = None,
        confidence_level: Optional[float] = None,
        raw_output: Optional[Any] = None,
        analyzed_at: Optional[datetime] = None,
        id: Optional[int] = None,
    ):
        self.id = id
        self.photograph_id = photograph_id
        self.status = status
        self.source_type = source_type
        self.location_type = location_type
        self.geographic_location = geographic_location
        self.latitude = latitude
        self.longitude = longitude
        self.location_radius_km = location_radius_km
        self.signage_found = signage_found
        self.architectural_landmarks = architectural_landmarks
        self.landscape_features = landscape_features
        self.analysis_provider = analysis_provider
        self.provider_version = provider_version
        self.confidence_level = confidence_level
        self.raw_output = raw_output
        self.analyzed_at = analyzed_at or datetime.utcnow()

    def __repr__(self) -> str:
        return (
            f"GeographicReference(id={self.id}, photograph_id={self.photograph_id}, "
            f"status={self.status}, location_type={self.location_type})"
        )


class EnvironmentalSpatial:
    """
    Domain entity for Attribute 04 — Environmental & Spatial Context.
    Accepts AI-generated and curator/user-contributed records.
    """

    def __init__(
        self,
        photograph_id: int,
        status: AttributeStatus = AttributeStatus.ACTIVE,
        source_type: SourceType = SourceType.AI,
        setting_type: Optional[str] = None,
        specific_typology: Optional[str] = None,
        conservation_state: Optional[str] = None,
        human_env_relationship: Optional[str] = None,
        analysis_provider: Optional[str] = None,
        provider_version: Optional[str] = None,
        confidence_level: Optional[float] = None,
        raw_output: Optional[Any] = None,
        analyzed_at: Optional[datetime] = None,
        id: Optional[int] = None,
    ):
        self.id = id
        self.photograph_id = photograph_id
        self.status = status
        self.source_type = source_type
        self.setting_type = setting_type
        self.specific_typology = specific_typology
        self.conservation_state = conservation_state
        self.human_env_relationship = human_env_relationship
        self.analysis_provider = analysis_provider
        self.provider_version = provider_version
        self.confidence_level = confidence_level
        self.raw_output = raw_output
        self.analyzed_at = analyzed_at or datetime.utcnow()

    def __repr__(self) -> str:
        return (
            f"EnvironmentalSpatial(id={self.id}, photograph_id={self.photograph_id}, "
            f"status={self.status}, setting_type={self.setting_type})"
        )
