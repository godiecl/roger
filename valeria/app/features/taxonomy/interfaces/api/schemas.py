"""
Pydantic schemas for the taxonomy feature API.
"""

from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel

from app.features.taxonomy.domain.taxonomy import AttributeStatus


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
