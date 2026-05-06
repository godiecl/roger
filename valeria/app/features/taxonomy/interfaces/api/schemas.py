"""
Pydantic schemas for the taxonomy feature API.
"""

from datetime import date, datetime
from typing import Any, List, Optional

from pydantic import BaseModel

from app.features.taxonomy.domain.taxonomy import AttributeStatus
from app.features.taxonomy.infrastructure.persistence.taxonomy_model import (
    DateType, LocationType, SettingType, ConservationState,
)


class TechnicalMetadataResponse(BaseModel):
    id: int
    photograph_id: int
    status: AttributeStatus
    film_format: Optional[str]
    manufacturer: Optional[str]
    emulsion_type: Optional[str]
    iso_sensitivity: Optional[str]
    mounting_marks: Optional[str]
    scanning_artifacts: Optional[str]
    physical_status: Optional[str]
    exposure: Optional[str]
    diaphragm_aperture: Optional[str]
    lens_optical: Optional[str]
    camera_settings: Optional[str]
    deterioration_notes: Optional[str]
    digitizer_person: Optional[str]
    is_estimated: bool
    analysis_provider: Optional[str]
    provider_version: Optional[str]
    confidence_level: Optional[float]
    raw_output: Optional[Any]
    analyzed_at: datetime

    model_config = {"from_attributes": True}


class TechnicalMetadataHistoryResponse(BaseModel):
    photograph_id: int
    total: int
    records: List[TechnicalMetadataResponse]


class AnalyzeResponse(BaseModel):
    message: str
    photograph_id: int
    record: TechnicalMetadataResponse


# ── Curator direct write schemas ───────────────────────────────────────────────

class ChronologyWriteRequest(BaseModel):
    date_type: Optional[DateType] = None
    precise_date: Optional[date] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    date_hypothesis: Optional[str] = None
    verification_source: Optional[str] = None
    methodology: Optional[str] = None
    visual_evidence_notes: Optional[str] = None


class ChronologyResponse(BaseModel):
    id: int
    photograph_id: int
    status: AttributeStatus
    date_type: Optional[DateType]
    precise_date: Optional[date]
    date_from: Optional[date]
    date_to: Optional[date]
    date_hypothesis: Optional[str]
    verification_source: Optional[str]
    methodology: Optional[str]
    visual_evidence_notes: Optional[str]
    analysis_provider: Optional[str]
    analyzed_at: datetime

    model_config = {"from_attributes": True}


class GeographicWriteRequest(BaseModel):
    location_type: Optional[LocationType] = None
    geographic_location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_radius_km: Optional[float] = None
    signage_found: Optional[str] = None
    architectural_landmarks: Optional[str] = None
    landscape_features: Optional[str] = None


class GeographicResponse(BaseModel):
    id: int
    photograph_id: int
    status: AttributeStatus
    location_type: Optional[LocationType]
    geographic_location: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    location_radius_km: Optional[float]
    signage_found: Optional[str]
    architectural_landmarks: Optional[str]
    landscape_features: Optional[str]
    analysis_provider: Optional[str]
    analyzed_at: datetime

    model_config = {"from_attributes": True}


class EnvironmentalWriteRequest(BaseModel):
    setting_type: Optional[SettingType] = None
    specific_typology: Optional[str] = None
    conservation_state: Optional[ConservationState] = None
    human_env_relationship: Optional[str] = None


class EnvironmentalResponse(BaseModel):
    id: int
    photograph_id: int
    status: AttributeStatus
    setting_type: Optional[SettingType]
    specific_typology: Optional[str]
    conservation_state: Optional[ConservationState]
    human_env_relationship: Optional[str]
    analysis_provider: Optional[str]
    analyzed_at: datetime

    model_config = {"from_attributes": True}
