from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class ContextResponse(BaseModel):
    id: int
    image_id: int
    text: str
    provider: str
    generation_time_ms: int
    is_anchored: bool
    anchored_by: Optional[int]
    anchored_at: Optional[datetime]
    like_count: int
    report_count: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class ContextListResponse(BaseModel):
    total: int
    contexts: List[ContextResponse]


class LikeResponse(BaseModel):
    liked: bool
    like_count: int


class ReportRequest(BaseModel):
    reason: Optional[str] = None


class PendingReportsCountResponse(BaseModel):
    count: int
