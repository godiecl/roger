"""
Stub analyzer for Attribute 03 — Geographic Reference.

Default when ATTR03_ANALYZER=stub (or unset). Creates an ACTIVE record
with location_type=unknown so the photograph appears in curator queues.
No external dependencies required.
"""

from app.infrastructure.analysis.base_analyzer import IAttributeAnalyzer

PROVIDER_NAME = "stub"
PROVIDER_VERSION = "1"


class StubGeographicAnalyzer(IAttributeAnalyzer):
    provider_name = PROVIDER_NAME
    provider_version = PROVIDER_VERSION

    def analyze(self, file_path: str) -> dict:
        return {
            "location_type": "unknown",
            "geographic_location": None,
            "latitude": None,
            "longitude": None,
            "location_radius_km": None,
            "signage_found": None,
            "architectural_landmarks": None,
            "landscape_features": None,
            "confidence": 0.0,
            "raw_output": None,
            "error": None,
            "provider": self.provider_name,
            "provider_version": self.provider_version,
        }
