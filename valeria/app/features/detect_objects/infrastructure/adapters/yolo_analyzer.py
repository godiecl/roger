"""
YOLOAnalyzer — detección de objetos + segmentación semántica con YOLOv8n-seg.

Satisface FONDEF Hito 3:
  - Componente 2: "reconocimiento de objetos mediante algoritmos de deep learning / computer vision"
  - Componente 3: "segmentación semántica de objetos de la colección patrimonial"

Modelo: yolov8n-seg (YOLOv8 nano segmentation — ~6.7 MB, COCO 80 clases).
Se descarga automáticamente en el primer uso al directorio de caché de ultralytics.

Dependencias: pip install ultralytics  (requirements-analyzers.txt)
Activación: el HybridAnalyzer lo selecciona cuando ultralytics está disponible y la
            imagen existe en disco. Si ultralytics no está instalado, el sistema cae a
            VisionAnalyzer (Claude Vision / GPT-4V).
"""

import json
import os
import time
from typing import Optional

import structlog

from app.features.detect_objects.domain.detection import (
    Detection, DetectedObject, DetectionStatus, ObjectCategory,
)
from app.features.detect_objects.domain.detection_port import IVisionAnalyzer

logger = structlog.get_logger()

PROVIDER_NAME = "yolov8n-seg"

# Mapeo COCO class → ObjectCategory
_COCO_TO_CATEGORY: dict[str, ObjectCategory] = {
    "person": ObjectCategory.PERSON,
    "bicycle": ObjectCategory.VEHICLE,
    "car": ObjectCategory.VEHICLE,
    "motorcycle": ObjectCategory.VEHICLE,
    "airplane": ObjectCategory.VEHICLE,
    "bus": ObjectCategory.VEHICLE,
    "train": ObjectCategory.VEHICLE,
    "truck": ObjectCategory.VEHICLE,
    "boat": ObjectCategory.VEHICLE,
    "horse": ObjectCategory.ANIMAL,
    "sheep": ObjectCategory.ANIMAL,
    "cow": ObjectCategory.ANIMAL,
    "elephant": ObjectCategory.ANIMAL,
    "bear": ObjectCategory.ANIMAL,
    "zebra": ObjectCategory.ANIMAL,
    "giraffe": ObjectCategory.ANIMAL,
    "dog": ObjectCategory.ANIMAL,
    "cat": ObjectCategory.ANIMAL,
    "bird": ObjectCategory.ANIMAL,
    "potted plant": ObjectCategory.VEGETATION,
    "tree": ObjectCategory.VEGETATION,
    "building": ObjectCategory.BUILDING,
    "bench": ObjectCategory.BUILDING,
    "chair": ObjectCategory.TOOL,
    "couch": ObjectCategory.TOOL,
    "dining table": ObjectCategory.TOOL,
    "backpack": ObjectCategory.TOOL,
    "umbrella": ObjectCategory.TOOL,
    "handbag": ObjectCategory.TOOL,
    "tie": ObjectCategory.TOOL,
    "suitcase": ObjectCategory.TOOL,
    "sports ball": ObjectCategory.TOOL,
    "kite": ObjectCategory.TOOL,
    "baseball bat": ObjectCategory.TOOL,
    "baseball glove": ObjectCategory.TOOL,
    "skateboard": ObjectCategory.VEHICLE,
    "surfboard": ObjectCategory.VEHICLE,
    "tennis racket": ObjectCategory.TOOL,
    "bottle": ObjectCategory.TOOL,
    "wine glass": ObjectCategory.TOOL,
    "cup": ObjectCategory.TOOL,
    "fork": ObjectCategory.TOOL,
    "knife": ObjectCategory.TOOL,
    "spoon": ObjectCategory.TOOL,
    "bowl": ObjectCategory.TOOL,
    "banana": ObjectCategory.VEGETATION,
    "apple": ObjectCategory.VEGETATION,
    "sandwich": ObjectCategory.TOOL,
    "orange": ObjectCategory.VEGETATION,
    "broccoli": ObjectCategory.VEGETATION,
    "carrot": ObjectCategory.VEGETATION,
    "book": ObjectCategory.TEXT,
    "clock": ObjectCategory.TOOL,
    "vase": ObjectCategory.TOOL,
    "scissors": ObjectCategory.TOOL,
    "teddy bear": ObjectCategory.TOOL,
    "hair drier": ObjectCategory.TOOL,
    "toothbrush": ObjectCategory.TOOL,
    "tv": ObjectCategory.TOOL,
    "laptop": ObjectCategory.TOOL,
    "mouse": ObjectCategory.TOOL,
    "remote": ObjectCategory.TOOL,
    "keyboard": ObjectCategory.TOOL,
    "cell phone": ObjectCategory.TOOL,
    "microwave": ObjectCategory.TOOL,
    "oven": ObjectCategory.TOOL,
    "toaster": ObjectCategory.TOOL,
    "sink": ObjectCategory.TOOL,
    "refrigerator": ObjectCategory.TOOL,
    "fire hydrant": ObjectCategory.BUILDING,
    "stop sign": ObjectCategory.TEXT,
    "parking meter": ObjectCategory.TOOL,
    "traffic light": ObjectCategory.TOOL,
    "bed": ObjectCategory.TOOL,
    "toilet": ObjectCategory.TOOL,
}


class YOLOAnalyzer(IVisionAnalyzer):
    """
    Detecta objetos y genera máscaras de segmentación usando YOLOv8n-seg.
    El modelo se descarga automáticamente la primera vez (~6.7 MB).
    """

    def __init__(self):
        self._model = None

    def _get_model(self):
        if self._model is None:
            try:
                from ultralytics import YOLO
                self._model = YOLO("yolov8n-seg.pt")
                logger.info("YOLOv8n-seg cargado", provider=PROVIDER_NAME)
            except ImportError as exc:
                raise RuntimeError(
                    "ultralytics no está instalado. "
                    "Ejecuta: pip install ultralytics  (requirements-analyzers.txt)"
                ) from exc
        return self._model

    @property
    def provider_name(self) -> str:
        return PROVIDER_NAME

    async def analyze(
        self,
        photograph_id: int,
        image_path: Optional[str] = None,
        image_url: Optional[str] = None,
    ) -> Detection:
        if not image_path or not os.path.isfile(image_path):
            raise ValueError(
                f"YOLOAnalyzer requiere image_path válido en disco. "
                f"Recibido: {image_path!r}"
            )

        start = time.time()
        try:
            objects, scene_description = self._run_inference(image_path)
            status = DetectionStatus.COMPLETED
        except Exception as e:
            logger.error("YOLOv8 inference fallida", error=str(e), photograph_id=photograph_id)
            objects = []
            scene_description = f"Análisis YOLO no disponible: {e}"
            status = DetectionStatus.FAILED

        return Detection(
            photograph_id=photograph_id,
            objects=objects,
            scene_description=scene_description,
            provider=self.provider_name,
            detection_time_ms=int((time.time() - start) * 1000),
            status=status,
        )

    def _run_inference(self, image_path: str) -> tuple[list[DetectedObject], str]:
        model = self._get_model()
        results = model(image_path, verbose=False)

        detected: list[DetectedObject] = []
        label_counts: dict[str, int] = {}

        for result in results:
            boxes = result.boxes
            masks = result.masks

            img_h, img_w = result.orig_shape

            for i, box in enumerate(boxes):
                class_id = int(box.cls[0])
                label = result.names[class_id]
                confidence = float(box.conf[0])

                # Bounding box normalizada (xyxy → 0-1)
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                bbox = (
                    round(x1 / img_w, 4),
                    round(y1 / img_h, 4),
                    round(x2 / img_w, 4),
                    round(y2 / img_h, 4),
                )

                # Polígono de segmentación (normalizado)
                mask_polygon = None
                if masks is not None and i < len(masks.xy):
                    poly = masks.xy[i]
                    if len(poly) > 0:
                        normalized = [
                            [round(float(pt[0]) / img_w, 4), round(float(pt[1]) / img_h, 4)]
                            for pt in poly
                        ]
                        mask_polygon = json.dumps(normalized)

                category = _COCO_TO_CATEGORY.get(label.lower(), ObjectCategory.OTHER)

                detected.append(DetectedObject(
                    label=label,
                    category=category,
                    confidence=round(confidence, 4),
                    description=None,
                    bbox=bbox,
                    mask_polygon=mask_polygon,
                ))

                label_counts[label] = label_counts.get(label, 0) + 1

        # Descripción de escena desde conteos detectados
        if label_counts:
            parts = [f"{label} ×{count}" for label, count in sorted(label_counts.items())]
            scene_description = f"Detección YOLOv8: {len(detected)} objetos — " + ", ".join(parts)
        else:
            scene_description = "No se detectaron objetos con suficiente confianza."

        return detected, scene_description
