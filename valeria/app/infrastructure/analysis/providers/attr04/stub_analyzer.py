"""
Stub analyzer for Attribute 04 — Environmental & Spatial Context.

Default when ATTR04_ANALYZER=stub (or unset). Creates an ACTIVE record
with null setting_type so the photograph appears in curator queues.
No external dependencies required.
"""

from app.infrastructure.analysis.base_analyzer import IAttributeAnalyzer

PROVIDER_NAME = "stub"
PROVIDER_VERSION = "1"


class StubEnvironmentalAnalyzer(IAttributeAnalyzer):
    provider_name = PROVIDER_NAME
    provider_version = PROVIDER_VERSION

    def analyze(self, file_path: str) -> dict:
        return {
            "setting_type": None,
            "specific_typology": None,
            "conservation_state": None,
            "human_env_relationship": None,
            "confidence": 0.0,
            "raw_output": None,
            "error": None,
            "provider": self.provider_name,
            "provider_version": self.provider_version,
        }
