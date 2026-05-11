"""
Groq Vision analyzer for Attribute 03 — Geographic Reference.

Usa llama-4-scout con visión para identificar el país y región de una fotografía
basándose en banderas, paisaje, arquitectura, vegetación y marcadores culturales.

Activate with: ATTR03_ANALYZER=groq in .env
"""

import os
from app.infrastructure.analysis.base_analyzer import IAttributeAnalyzer
from app.infrastructure.analysis.providers.groq_vision_base import (
    call_groq_vision, _parse_json_response
)

PROVIDER_NAME = "groq_vision"
PROVIDER_VERSION = "llama-4-scout"

_SYSTEM = (
    "Eres un experto en análisis geográfico de fotografía histórica latinoamericana. "
    "Respondes ÚNICAMENTE con JSON válido, sin texto adicional ni markdown."
)

_USER = """Analiza esta fotografía histórica para determinar dónde fue tomada.

Busca estas pistas:
- Banderas nacionales o emblemas (bandera chilena, boliviana, peruana, etc.)
- Texto visible, letreros o inscripciones (idioma, topónimos)
- Tipo de paisaje y vegetación (Andes, desierto Atacama, valle central, altiplano, costa)
- Estilos arquitectónicos típicos de cada región
- Marcadores culturales (ropa tradicional, costumbres)
- Características geográficas (montañas nevadas, cordillera, mar, lago, río)
- Fauna y flora característica

Responde SOLO con este JSON exacto:
{
  "location_type": "precise" | "approximate" | "unknown",
  "geographic_location": "descripción del lugar o null",
  "country": "nombre del país o null",
  "region": "región o ciudad o null",
  "confidence": 0.0,
  "visual_evidence": ["lista", "de", "pistas", "encontradas"]
}"""


class GroqGeographicAnalyzer(IAttributeAnalyzer):
    provider_name = PROVIDER_NAME
    provider_version = PROVIDER_VERSION

    def __init__(self) -> None:
        self._api_key = os.getenv("GROQ_API_KEY", "")
        if not self._api_key:
            raise ValueError(
                "GroqGeographicAnalyzer requiere GROQ_API_KEY en el .env"
            )

    def analyze(self, file_path: str) -> dict:
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}", "provider": self.provider_name, "provider_version": self.provider_version}
        try:
            raw = call_groq_vision(self._api_key, _SYSTEM, _USER, file_path)
            data = _parse_json_response(raw)
            country = data.get("country")
            region = data.get("region")
            location = data.get("geographic_location") or ", ".join(filter(None, [region, country]))
            return {
                "location_type": data.get("location_type", "unknown"),
                "geographic_location": location,
                "latitude": None,
                "longitude": None,
                "location_radius_km": None,
                "signage_found": None,
                "architectural_landmarks": None,
                "landscape_features": ", ".join(data.get("visual_evidence", [])),
                "confidence": float(data.get("confidence", 0.0)),
                "raw_output": data,
                "error": None,
                "provider": self.provider_name,
                "provider_version": self.provider_version,
            }
        except Exception as exc:
            return {"error": str(exc), "provider": self.provider_name, "provider_version": self.provider_version}
