from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.features.contributions.domain.contribution import ContributionAttributeType, ContributionStatus


class ContributionCreateRequest(BaseModel):
    photograph_id: int
    attribute_type: ContributionAttributeType
    field_name: str = Field(..., min_length=1)
    proposed_value: str = Field(..., min_length=1)
    evidence_notes: Optional[str] = None


class RejectRequest(BaseModel):
    rejection_reason: Optional[str] = None


class ContributionResponse(BaseModel):
    id: int
    photograph_id: int
    contributor_id: Optional[int]
    attribute_type: ContributionAttributeType
    field_name: str
    proposed_value: str
    evidence_notes: Optional[str]
    status: ContributionStatus
    reviewed_by: Optional[int]
    reviewed_at: Optional[datetime]
    rejection_reason: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class ContributionListResponse(BaseModel):
    total: int
    contributions: List[ContributionResponse]
