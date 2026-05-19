from datetime import datetime
from typing import List, Literal, Optional

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
    bbox: Optional[List[float]] = None
    mask_polygon: Optional[str] = None


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


# --- Anotaciones de experto (FONDEF Hito 2) ---

class ExpertDetectionAnnotationCreate(BaseModel):
    detected_object_id: Optional[int] = Field(
        default=None,
        description="ID del objeto detectado a anotar. None = objeto faltante no detectado por la IA.",
    )
    verdict: Literal["correct", "incorrect", "uncertain"] = Field(
        description="Veredicto del experto sobre la detección"
    )
    corrected_label: Optional[str] = Field(
        default=None,
        description="Etiqueta corregida si verdict=incorrect",
    )
    corrected_category: Optional[str] = Field(
        default=None,
        description="Categoría corregida si verdict=incorrect",
    )
    notes: Optional[str] = None


class ExpertDetectionAnnotationResponse(BaseModel):
    id: int
    detection_id: int
    detected_object_id: Optional[int]
    annotator_id: int
    verdict: str
    corrected_label: Optional[str]
    corrected_category: Optional[str]
    notes: Optional[str]
    created_at: datetime


class ExpertDetectionAnnotationListResponse(BaseModel):
    total: int
    annotations: List[ExpertDetectionAnnotationResponse]


class ExpertDescriptionAnnotationCreate(BaseModel):
    ai_rating: Optional[int] = Field(
        default=None,
        ge=1,
        le=5,
        description="Calidad de la descripción generada por IA (1=muy mala … 5=excelente)",
    )
    reference_description: str = Field(
        description="Descripción de referencia escrita por el experto (ground truth)"
    )
    notes: Optional[str] = None


class ExpertDescriptionAnnotationResponse(BaseModel):
    id: int
    photograph_id: int
    annotator_id: int
    ai_rating: Optional[int]
    reference_description: str
    notes: Optional[str]
    created_at: datetime


# --- Métricas de evaluación FONDEF (Phase 5) ---

class MetricResult(BaseModel):
    value: Optional[float]         # valor calculado (None = datos insuficientes)
    target: float                  # umbral FONDEF
    passes: Optional[bool]         # None = insuficientes datos
    label: str
    description: str
    detail: dict                   # estadísticas de soporte


class AnnotationCoverage(BaseModel):
    detections_total: int
    detections_annotated: int
    detection_coverage_pct: float
    descriptions_total: int
    descriptions_annotated: int
    description_coverage_pct: float
    total_detection_annotations: int
    total_description_annotations: int


class EvaluationMetricsResponse(BaseModel):
    ica1: MetricResult
    ica2: MetricResult
    ica3: MetricResult
    ica4: MetricResult
    coverage: AnnotationCoverage
    sufficient_data: bool
    computed_at: datetime
