from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class DetectRequest(BaseModel):
    photograph_id: int
    image_path: Optional[str] = Field(
        default=None,
        description="Ruta relativa al STORAGE_PATH del archivo de imagen (JPG/PNG/TIFF)"
    )
    image_url: Optional[str] = Field(
        default=None,
        description="URL pública de la imagen (alternativa a image_path)"
    )
    force_reanalysis: bool = Field(
        default=False,
        description="Si True, re-analiza aunque ya exista una detección para esta fotografía"
    )


class DetectedObjectResponse(BaseModel):
    id: Optional[int]
    label: str
    category: str
    confidence: float
    description: Optional[str]


class DetectionResponse(BaseModel):
    id: Optional[int]
    photograph_id: int
    scene_description: str
    provider: str
    detection_time_ms: int
    status: str
    object_count: int
    objects: List[DetectedObjectResponse]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class DetectionListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    detections: List[DetectionResponse]
