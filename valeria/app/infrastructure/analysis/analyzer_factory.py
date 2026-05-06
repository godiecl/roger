"""
Factory functions for attribute analyzers 02, 03, and 04.

Select the active provider via .env — no code changes needed to switch tools:

  ATTR02_ANALYZER=stub      # no-op, zero confidence (default)
  ATTR02_ANALYZER=clip      # CLIP zero-shot decade classification

  ATTR03_ANALYZER=stub      # no-op, zero confidence (default)
  ATTR03_ANALYZER=geoclip   # GeoCLIP geographic localization

  ATTR04_ANALYZER=stub      # no-op, zero confidence (default)
  ATTR04_ANALYZER=places365 # Places365 scene classification

The factory imports the concrete provider lazily, so missing optional
dependencies (torch, open_clip, geoclip) never break the default stub path.
"""

from app.infrastructure.analysis.base_analyzer import IAttributeAnalyzer
from app.config.settings import settings


def create_chronology_analyzer() -> IAttributeAnalyzer:
    """Return the configured analyzer for Attribute 02 (Chronological Dating)."""
    if settings.attr02_analyzer.lower().strip() == "clip":
        from app.infrastructure.analysis.providers.attr02.clip_temporal_analyzer import (
            CLIPTemporalAnalyzer,
        )
        return CLIPTemporalAnalyzer()
    from app.infrastructure.analysis.providers.attr02.stub_analyzer import StubChronologyAnalyzer
    return StubChronologyAnalyzer()


def create_geographic_analyzer() -> IAttributeAnalyzer:
    """Return the configured analyzer for Attribute 03 (Geographic Reference)."""
    if settings.attr03_analyzer.lower().strip() == "geoclip":
        from app.infrastructure.analysis.providers.attr03.geoclip_analyzer import (
            GeoCLIPAnalyzer,
        )
        return GeoCLIPAnalyzer()
    from app.infrastructure.analysis.providers.attr03.stub_analyzer import StubGeographicAnalyzer
    return StubGeographicAnalyzer()


def create_environmental_analyzer() -> IAttributeAnalyzer:
    """Return the configured analyzer for Attribute 04 (Environmental & Spatial Context)."""
    if settings.attr04_analyzer.lower().strip() == "places365":
        from app.infrastructure.analysis.providers.attr04.places365_analyzer import (
            Places365Analyzer,
        )
        return Places365Analyzer()
    from app.infrastructure.analysis.providers.attr04.stub_analyzer import StubEnvironmentalAnalyzer
    return StubEnvironmentalAnalyzer()
