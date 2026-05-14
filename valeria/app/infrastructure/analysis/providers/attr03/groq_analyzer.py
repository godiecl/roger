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
    "Conoces en detalle las banderas y símbolos nacionales de todos los países de América Latina. "
    "Respondes ÚNICAMENTE con JSON válido, sin texto adicional ni markdown."
)

_USER = """Analiza esta fotografía histórica para determinar dónde fue tomada.

IDENTIFICACIÓN DE BANDERAS — prioridad máxima:
La bandera chilena tiene: cuadrado azul con estrella blanca en el cantón superior izquierdo,
franja blanca horizontal y franja roja horizontal. Es distinta a la española (no tiene escudo central).
Si ves esa bandera → país = Chile.

Otras banderas latinoamericanas:
- Bolivia: franja horizontal roja, amarilla, verde (sin escudo = estado; con escudo = gobierno)
- Perú: franjas verticales rojo-blanco-rojo
- Argentina: franjas horizontales celeste-blanco-celeste con sol
- Uruguay: franjas horizontales blancas y azules con sol
- Colombia/Ecuador/Venezuela: amarillo-azul-rojo horizontal

OTRAS PISTAS A BUSCAR:
- Texto visible, letreros o inscripciones (idioma, topónimos)
- Paisaje y vegetación: Andes con nieve, desierto Atacama, valle central chileno, altiplano, costa Pacífico
- Estilos arquitectónicos típicos de cada región
- Marcadores culturales (ropa, costumbres, eventos)
- Características geográficas (cordillera, mar, lago, río)
- Fauna característica (cóndor, llama, guanaco)

IMPORTANTE: Esta colección fotográfica es latinoamericana. Si ves la bandera chilena, la respuesta
es Chile aunque el paisaje o las personas puedan parecer de otro lugar.

Responde SOLO con este JSON exacto:
{
  "location_type": "precise" | "approximate" | "unknown",
  "geographic_location": "descripción del lugar o null",
  "country": "nombre del país o null",
  "region": "región o ciudad o null",
  "signage_found": "texto visible en letreros o inscripciones, o null si no hay",
  "architectural_landmarks": "edificios o hitos arquitectónicos identificables, o null si no hay",
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
                "signage_found": data.get("signage_found"),
                "architectural_landmarks": data.get("architectural_landmarks"),
                "landscape_features": ", ".join(data.get("visual_evidence", [])),
                "confidence": float(data.get("confidence", 0.0)),
                "raw_output": data,
                "error": None,
                "provider": self.provider_name,
                "provider_version": self.provider_version,
            }
        except Exception as exc:
            return {"error": str(exc), "provider": self.provider_name, "provider_version": self.provider_version}
