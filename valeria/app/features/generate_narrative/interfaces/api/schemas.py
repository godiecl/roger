"""
Pydantic schemas for narrative API
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SourceResponse(BaseModel):
    """Source response schema."""
    text: str
    source_type: str  # "veraz" or "verosímil"
    reference: Optional[str] = None
    relevance_score: Optional[float] = None


class TrazabilidadResponse(BaseModel):
    """Trazabilidad response schema."""
    sources: List[SourceResponse]
    primary_source_type: str
    confidence_score: float
    verified_sources_count: int
    plausible_sources_count: int


class NarrativeResponse(BaseModel):
    """Narrative response schema."""
    id: int
    image_id: int
    text: str
    trazabilidad: TrazabilidadResponse
    user_id: Optional[int]
    prompt: Optional[str]
    language: str
    model_used: Optional[str]
    generation_time_ms: Optional[int]
    is_approved: bool
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    is_verified: bool
    confidence_level: str  # "high", "medium", "low"
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NarrativeListResponse(BaseModel):
    """Narrative list response schema."""
    total: int
    skip: int
    limit: int
    narratives: List[NarrativeResponse]


class GenerateNarrativeRequest(BaseModel):
    """Request to generate a narrative."""
    image_id: int = Field(..., description="ID of the image")
    prompt: Optional[str] = Field(None, max_length=1000, description="Custom prompt for generation")
    language: str = Field("es", pattern="^(es|en|de)$", description="Language code (es, en, de)")


class RegenerateNarrativeRequest(BaseModel):
    """Request to regenerate a narrative."""
    prompt: Optional[str] = Field(None, max_length=1000, description="New prompt for regeneration")


class ApproveNarrativeRequest(BaseModel):
    """Request to approve a narrative."""
    approved_by: int = Field(..., description="ID of user approving")
