"""
Stub analyzer for Attribute 02 — Chronological Dating.

Default when ATTR02_ANALYZER=stub (or unset). Creates an ACTIVE record
with date_type=unknown so the photograph appears in curator queues as
needing manual or AI-assisted dating. No external dependencies required.
"""

from app.infrastructure.analysis.base_analyzer import IAttributeAnalyzer

PROVIDER_NAME = "stub"
PROVIDER_VERSION = "1"


class StubChronologyAnalyzer(IAttributeAnalyzer):
    provider_name = PROVIDER_NAME
    provider_version = PROVIDER_VERSION

    def analyze(self, file_path: str) -> dict:
        return {
            "date_type": "unknown",
            "precise_date": None,
            "date_from": None,
            "date_to": None,
            "date_hypothesis": None,
            "methodology": (
                "Stub analyzer — no temporal analysis provider configured. "
                "Set ATTR02_ANALYZER=clip in .env to enable CLIP-based dating."
            ),
            "visual_evidence_notes": None,
            "confidence": 0.0,
            "raw_output": None,
            "error": None,
            "provider": self.provider_name,
            "provider_version": self.provider_version,
        }
