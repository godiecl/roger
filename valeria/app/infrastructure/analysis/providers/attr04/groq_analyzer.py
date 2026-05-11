"""
Groq Vision analyzer for Attribute 04 — Environmental & Spatial Context.

Usa llama-4-scout con visión para clasificar el ambiente, tipo de escena
y objetos presentes en la fotografía.

Activate with: ATTR04_ANALYZER=groq in .env
"""

import os
from app.infrastructure.analysis.base_analyzer import IAttributeAnalyzer
from app.infrastructure.analysis.providers.groq_vision_base import (
    call_groq_vision, _parse_json_response
)

PROVIDER_NAME = "groq_vision"
PROVIDER_VERSION = "llama-4-scout"

_SYSTEM = (
    "Eres un experto en análisis visual de fotografía histórica latinoamericana. "
    "Respondes ÚNICAMENTE con JSON válido, sin texto adicional ni markdown."
)

_USER = """Analiza el contexto ambiental y espacial de esta fotografía histórica.

Identifica:
- Ambientación: interior o exterior
- Tipo de entorno: urbano, rural, natural, industrial, mixto
- Tipología específica: calle, plaza, campo, costa, montaña, casa, iglesia, etc.
- Objetos y seres presentes: personas, animales (caballos, ganado), vehículos, edificios
- Estado de conservación del entorno: prístino, antropogénico, modificado, degradado
- Relación humano-entorno: procesión, trabajo agrícola, retrato, paisaje, etc.

Responde SOLO con este JSON exacto:
{
  "setting_type": "urban" | "rural" | "natural" | "industrial" | "interior" | "mixed",
  "specific_typology": "descripción específica de la escena",
  "conservation_state": "pristine" | "anthropogenic" | "modified" | "degraded",
  "objects_detected": ["lista", "de", "objetos", "y", "seres", "presentes"],
  "human_env_relationship": "descripción de la actividad o null",
  "confidence": 0.0
}"""


class GroqEnvironmentalAnalyzer(IAttributeAnalyzer):
    provider_name = PROVIDER_NAME
    provider_version = PROVIDER_VERSION

    def __init__(self) -> None:
        self._api_key = os.getenv("GROQ_API_KEY", "")
        if not self._api_key:
            raise ValueError(
                "GroqEnvironmentalAnalyzer requiere GROQ_API_KEY en el .env"
            )

    def analyze(self, file_path: str) -> dict:
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}", "provider": self.provider_name, "provider_version": self.provider_version}
        try:
            raw = call_groq_vision(self._api_key, _SYSTEM, _USER, file_path)
            data = _parse_json_response(raw)
            return {
                "setting_type": data.get("setting_type"),
                "specific_typology": data.get("specific_typology"),
                "conservation_state": data.get("conservation_state"),
                "human_env_relationship": data.get("human_env_relationship"),
                "objects_detected": data.get("objects_detected", []),
                "confidence": float(data.get("confidence", 0.0)),
                "raw_output": data,
                "error": None,
                "provider": self.provider_name,
                "provider_version": self.provider_version,
            }
        except Exception as exc:
            return {"error": str(exc), "provider": self.provider_name, "provider_version": self.provider_version}
