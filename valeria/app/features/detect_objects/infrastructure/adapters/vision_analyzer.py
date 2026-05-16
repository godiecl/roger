"""
VisionAnalyzer — detecta objetos en fotografías usando Claude Vision o GPT-4V.

Prioridad: Anthropic (si ANTHROPIC_API_KEY configurada) → OpenAI (si OPENAI_API_KEY configurada).
No requiere dependencias locales pesadas (sin YOLO/torch).
"""

import base64
import json
import os
import time
from pathlib import Path
from typing import Optional, Tuple

import structlog

from app.features.detect_objects.domain.detection import (
    Detection, DetectedObject, DetectionStatus, ObjectCategory,
)
from app.features.detect_objects.domain.detection_port import IVisionAnalyzer
from app.config.settings import settings

logger = structlog.get_logger()

_DETECTION_PROMPT = """Analiza esta fotografía histórica de la colección de Robert Gerstmann y detecta todos los objetos, personas, elementos y características visibles.

Responde ÚNICAMENTE con un JSON válido en este formato, sin texto adicional:
{
  "scene_description": "Descripción general de la escena en español (2-3 oraciones)",
  "objects": [
    {
      "label": "nombre del objeto en español",
      "category": "person|animal|building|landscape|tool|vehicle|vegetation|text|other",
      "confidence": 0.95,
      "description": "descripción breve del elemento"
    }
  ]
}

Categorías:
- person: personas, figuras humanas
- animal: animales, ganado
- building: edificios, estructuras, ruinas, instalaciones
- landscape: montañas, ríos, valles, terreno
- tool: herramientas, maquinaria, equipo técnico
- vehicle: barcos, trenes, carretas, vehículos
- vegetation: árboles, plantas, cultivos
- text: carteles, letreros, inscripciones visibles
- other: cualquier otro elemento notable

Incluye todos los elementos visibles, incluso los de fondo. Confidence entre 0.0 y 1.0."""


class VisionAnalyzer(IVisionAnalyzer):
    """
    Analiza fotografías usando Claude Vision o GPT-4V.
    Selecciona el proveedor según las API keys disponibles en settings.
    """

    def __init__(self):
        self._provider: str = ""
        self._model: str = ""
        self._client = None
        self._init_provider()

    def _init_provider(self) -> None:
        if settings.anthropic_api_key:
            try:
                import anthropic
                self._client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
                self._provider = "anthropic"
                self._model = settings.anthropic_model or "claude-3-5-sonnet-20241022"
                logger.info("VisionAnalyzer inicializado con Anthropic Claude Vision", model=self._model)
                return
            except ImportError:
                logger.warning("Paquete 'anthropic' no instalado, intentando OpenAI")

        if settings.openai_api_key:
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(api_key=settings.openai_api_key)
                self._provider = "openai"
                self._model = settings.openai_model or "gpt-4o"
                logger.info("VisionAnalyzer inicializado con OpenAI Vision", model=self._model)
                return
            except ImportError:
                logger.warning("Paquete 'openai' no instalado")

        raise RuntimeError(
            "VisionAnalyzer requiere ANTHROPIC_API_KEY u OPENAI_API_KEY configuradas en el .env"
        )

    @property
    def provider_name(self) -> str:
        return f"{self._provider}/{self._model}"

    async def analyze(
        self,
        photograph_id: int,
        image_path: Optional[str] = None,
        image_url: Optional[str] = None,
    ) -> Detection:
        start = time.time()

        try:
            image_data, media_type = self._load_image(image_path, image_url)
            raw_response = await self._call_vision(image_data, media_type, image_url)
            objects, scene_description = self._parse_response(raw_response)
            status = DetectionStatus.COMPLETED
        except Exception as e:
            logger.error("Análisis de visión fallido", error=str(e), photograph_id=photograph_id)
            objects = []
            scene_description = f"Análisis no disponible: {str(e)}"
            status = DetectionStatus.FAILED

        return Detection(
            photograph_id=photograph_id,
            objects=objects,
            scene_description=scene_description,
            provider=self.provider_name,
            detection_time_ms=int((time.time() - start) * 1000),
            status=status,
        )

    def _load_image(
        self,
        image_path: Optional[str],
        image_url: Optional[str],
    ) -> Tuple[Optional[str], Optional[str]]:
        if image_url:
            return None, None

        if not image_path:
            raise ValueError("Se requiere image_path o image_url para el análisis")

        full_path = (
            Path(image_path)
            if os.path.isabs(image_path)
            else Path(settings.storage_path) / image_path
        )

        if not full_path.exists():
            raise FileNotFoundError(f"Archivo de imagen no encontrado: {full_path}")

        media_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".tiff": "image/tiff",
            ".tif": "image/tiff",
        }
        media_type = media_types.get(full_path.suffix.lower(), "image/jpeg")

        with open(full_path, "rb") as f:
            image_data = base64.standard_b64encode(f.read()).decode("utf-8")

        return image_data, media_type

    async def _call_vision(
        self,
        image_data: Optional[str],
        media_type: Optional[str],
        image_url: Optional[str],
    ) -> str:
        if self._provider == "anthropic":
            return await self._call_anthropic(image_data, media_type, image_url)
        return await self._call_openai(image_data, media_type, image_url)

    async def _call_anthropic(
        self,
        image_data: Optional[str],
        media_type: Optional[str],
        image_url: Optional[str],
    ) -> str:
        if image_url:
            image_block = {"type": "image", "source": {"type": "url", "url": image_url}}
        else:
            image_block = {
                "type": "image",
                "source": {"type": "base64", "media_type": media_type, "data": image_data},
            }

        response = await self._client.messages.create(
            model=self._model,
            max_tokens=2000,
            messages=[
                {"role": "user", "content": [image_block, {"type": "text", "text": _DETECTION_PROMPT}]}
            ],
        )
        return response.content[0].text

    async def _call_openai(
        self,
        image_data: Optional[str],
        media_type: Optional[str],
        image_url: Optional[str],
    ) -> str:
        if image_url:
            img_block = {"type": "image_url", "image_url": {"url": image_url}}
        else:
            img_block = {
                "type": "image_url",
                "image_url": {"url": f"data:{media_type};base64,{image_data}"},
            }

        response = await self._client.chat.completions.create(
            model=self._model,
            max_tokens=2000,
            messages=[
                {"role": "user", "content": [img_block, {"type": "text", "text": _DETECTION_PROMPT}]}
            ],
        )
        return response.choices[0].message.content

    def _parse_response(self, raw: str) -> Tuple[list, str]:
        raw = raw.strip()
        # Remover bloques markdown si el modelo los incluye
        if raw.startswith("```"):
            lines = raw.split("\n")
            raw = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

        data = json.loads(raw)
        scene_description = data.get("scene_description", "")

        objects = []
        for obj in data.get("objects", []):
            try:
                category = ObjectCategory(obj.get("category", "other"))
            except ValueError:
                category = ObjectCategory.OTHER

            objects.append(DetectedObject(
                label=obj.get("label", ""),
                category=category,
                confidence=min(max(float(obj.get("confidence", 1.0)), 0.0), 1.0),
                description=obj.get("description"),
            ))

        return objects, scene_description
