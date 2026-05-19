from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


class DetectionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class ObjectCategory(str, Enum):
    PERSON = "person"
    ANIMAL = "animal"
    BUILDING = "building"
    LANDSCAPE = "landscape"
    TOOL = "tool"
    VEHICLE = "vehicle"
    VEGETATION = "vegetation"
    TEXT = "text"
    OTHER = "other"


@dataclass
class DetectedObject:
    label: str
    category: ObjectCategory
    confidence: float
    description: Optional[str] = None
    # Bounding box normalizada [0-1]: (x1, y1, x2, y2)
    bbox: Optional[tuple] = None
    # Polígono de segmentación como JSON: [[x1,y1],[x2,y2],...]
    mask_polygon: Optional[str] = None
    id: Optional[int] = None


@dataclass
class Detection:
    photograph_id: int
    objects: List[DetectedObject]
    scene_description: str
    provider: str
    detection_time_ms: int
    status: DetectionStatus = DetectionStatus.COMPLETED
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def object_count(self) -> int:
        return len(self.objects)

    def objects_by_category(self, category: ObjectCategory) -> List[DetectedObject]:
        return [o for o in self.objects if o.category == category]
