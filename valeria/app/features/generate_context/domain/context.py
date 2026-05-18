from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class ImageContext:
    image_id: int
    text: str
    provider: str
    generation_time_ms: int = 0
    is_anchored: bool = False
    anchored_by: Optional[int] = None
    anchored_at: Optional[datetime] = None
    like_count: int = 0
    report_count: int = 0
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
