"""
Taxonomy domain entities for ROGER - Valeria API.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional


class AttributeStatus(str, Enum):
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    PENDING = "pending"


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
