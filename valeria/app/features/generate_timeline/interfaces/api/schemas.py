from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class GenerateTimelineRequest(BaseModel):
    photograph_id: int
    photograph_date: Optional[str] = Field(
        default=None,
        description="Fecha aproximada de la fotografía (ej. 'Octubre 1928', '1930s')"
    )
    photograph_location: Optional[str] = Field(
        default=None,
        description="Ubicación donde se tomó la fotografía"
    )
    photograph_description: Optional[str] = Field(
        default=None,
        description="Descripción o título de la fotografía"
    )
    detected_objects: Optional[List[str]] = Field(
        default=None,
        description="Objetos detectados en la fotografía (para enriquecer el contexto)"
    )
    force_regeneration: bool = Field(
        default=False,
        description="Si True, genera una nueva timeline aunque ya exista una"
    )


class ApproveTimelineRequest(BaseModel):
    approved_by: int


class TimelineEventResponse(BaseModel):
    id: Optional[int]
    date_label: str
    year: Optional[int]
    title: str
    description: str
    axis: str
    event_type: str
    source_type: str


class TimelineResponse(BaseModel):
    id: Optional[int]
    photograph_id: int
    context_summary: str
    provider: str
    generation_time_ms: int
    is_approved: bool
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    event_count: int
    events: List[TimelineEventResponse]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class TimelineListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    timelines: List[TimelineResponse]
