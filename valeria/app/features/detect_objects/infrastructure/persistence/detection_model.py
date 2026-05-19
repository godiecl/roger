from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, Enum as SQLEnum, JSON

from app.infrastructure.database.base import BaseModel
from app.features.detect_objects.domain.detection import DetectionStatus, ObjectCategory


def _enum_values(x):
    return [e.value for e in x]


class ObjectDetectionModel(BaseModel):
    """Resultado de un análisis de detección de objetos sobre una fotografía."""

    __tablename__ = "object_detections"

    photograph_id = Column(
        Integer, ForeignKey("photographs.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    provider = Column(String(150), nullable=False)
    scene_description = Column(Text, nullable=True)
    detection_time_ms = Column(Integer, nullable=True)
    status = Column(
        SQLEnum(DetectionStatus, values_callable=_enum_values),
        nullable=False,
        default=DetectionStatus.COMPLETED,
    )

    def __repr__(self) -> str:
        return f"<ObjectDetectionModel(id={self.id}, photograph_id={self.photograph_id}, status={self.status})>"


class DetectedObjectModel(BaseModel):
    """Objeto individual detectado dentro de un análisis."""

    __tablename__ = "detected_objects"

    detection_id = Column(
        Integer, ForeignKey("object_detections.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    label = Column(String(255), nullable=False)
    category = Column(
        SQLEnum(ObjectCategory, values_callable=_enum_values),
        nullable=False,
    )
    confidence = Column(Float, nullable=False, default=1.0)
    description = Column(Text, nullable=True)
    # Bounding box normalizada (YOLO xyxy 0-1)
    bbox_x1 = Column(Float, nullable=True)
    bbox_y1 = Column(Float, nullable=True)
    bbox_x2 = Column(Float, nullable=True)
    bbox_y2 = Column(Float, nullable=True)
    # Polígono de segmentación en JSON [[x,y],...]
    mask_polygon = Column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<DetectedObjectModel(id={self.id}, label={self.label}, category={self.category})>"


class ExpertDetectionAnnotationModel(BaseModel):
    """Anotación de experto sobre un objeto detectado por IA (FONDEF ICa1/ICa2)."""

    __tablename__ = "expert_detection_annotations"

    detection_id = Column(
        Integer, ForeignKey("object_detections.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    # None → anotación de "objeto faltante no detectado por la IA"
    detected_object_id = Column(
        Integer, ForeignKey("detected_objects.id", ondelete="CASCADE"),
        nullable=True, index=True,
    )
    annotator_id = Column(Integer, nullable=False, index=True)
    verdict = Column(String(20), nullable=False)          # correct | incorrect | uncertain
    corrected_label = Column(String(255), nullable=True)
    corrected_category = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)


class ExpertDescriptionAnnotationModel(BaseModel):
    """Descripción de referencia escrita por un experto para una fotografía (FONDEF ICa3)."""

    __tablename__ = "expert_description_annotations"

    photograph_id = Column(
        Integer, ForeignKey("photographs.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    annotator_id = Column(Integer, nullable=False, index=True)
    ai_rating = Column(Integer, nullable=True)            # 1-5: calidad de la descripción IA
    reference_description = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)
