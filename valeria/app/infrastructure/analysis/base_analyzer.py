"""
Abstract interface for attribute analyzers in ROGER.

Every analyzer — technical, chronological, geographic, environmental —
must implement this interface so use cases work against an abstract type
and concrete providers are swappable via .env configuration.

Contract for analyze():
- Never raises.
- Always returns a dict with 'provider' and 'provider_version' keys.
- On error, returns {'error': '<message>', 'provider': ..., 'provider_version': ...}.
- On success, 'error' is None.
"""

from abc import ABC, abstractmethod


class IAttributeAnalyzer(ABC):
    """Base class for all attribute analyzers."""

    provider_name: str = ""
    provider_version: str = ""

    @abstractmethod
    def analyze(self, file_path: str) -> dict:
        """
        Analyze a photograph file and return structured attribute data.
        Must never raise — errors go in the 'error' key.
        """
        ...
