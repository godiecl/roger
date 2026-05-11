"""
Groq Vision analyzer for Attribute 02 — Chronological Dating.

Usa llama-4-scout con visión para estimar la década de una fotografía
basándose en técnica fotográfica, vestimenta, tecnología y contexto visual.

Activate with: ATTR02_ANALYZER=groq in .env
"""

import os
from app.infrastructure.analysis.base_analyzer import IAttributeAnalyzer
from app.infrastructure.analysis.providers.groq_vision_base import (
    call_groq_vision, _parse_json_response
)

PROVIDER_NAME = "groq_vision"
PROVIDER_VERSION = "llama-4-scout"

_SYSTEM = (
    "Eres un experto en análisis de fotografía histórica latinoamericana. "
    "Respondes ÚNICAMENTE con JSON válido, sin texto adicional ni markdown."
)

_USER = """Analiza esta fotografía histórica y determina su período temporal aproximado.

Busca estas pistas:
- Técnica fotográfica: B&W/sepia indica pre-1960, color indica post-1950
- Estilos de ropa y moda
- Vehículos, maquinaria, tecnología visible
- Estilos arquitectónicos
- Animales de trabajo (caballos, bueyes) vs vehículos motorizados
- Objetos culturales y artefactos

Responde SOLO con este JSON exacto:
{
  "date_type": "precise" | "range" | "unknown",
  "precise_date": null,
  "date_from": "YYYY-01-01",
  "date_to": "YYYY-12-31",
  "date_hypothesis": "Explicación breve de la evidencia encontrada",
  "confidence": 0.0,
  "visual_evidence": ["lista", "de", "pistas", "encontradas"]
}"""


class GroqChronologyAnalyzer(IAttributeAnalyzer):
    provider_name = PROVIDER_NAME
    provider_version = PROVIDER_VERSION

    def __init__(self) -> None:
        self._api_key = os.getenv("GROQ_API_KEY", "")
        if not self._api_key:
            raise ValueError(
                "GroqChronologyAnalyzer requiere GROQ_API_KEY en el .env"
            )

    def analyze(self, file_path: str) -> dict:
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}", "provider": self.provider_name, "provider_version": self.provider_version}
        try:
            raw = call_groq_vision(self._api_key, _SYSTEM, _USER, file_path)
            data = _parse_json_response(raw)
            return {
                "date_type": data.get("date_type", "unknown"),
                "precise_date": data.get("precise_date"),
                "date_from": data.get("date_from"),
                "date_to": data.get("date_to"),
                "date_hypothesis": data.get("date_hypothesis"),
                "methodology": f"Groq Vision / {PROVIDER_VERSION}",
                "visual_evidence_notes": ", ".join(data.get("visual_evidence", [])),
                "confidence": float(data.get("confidence", 0.0)),
                "raw_output": data,
                "error": None,
                "provider": self.provider_name,
                "provider_version": self.provider_version,
            }
        except Exception as exc:
            return {"error": str(exc), "provider": self.provider_name, "provider_version": self.provider_version}
