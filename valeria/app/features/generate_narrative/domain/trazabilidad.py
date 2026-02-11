"""
Trazabilidad (Traceability) value object
"""
from enum import Enum
from typing import List, Optional
from dataclasses import dataclass


class SourceType(str, Enum):
    """Source type for narrative generation."""
    VERAZ = "veraz"  # Verified source (from known historical documents)
    VEROSIMIL = "verosímil"  # Plausible source (AI-generated or inferred)


@dataclass(frozen=True)
class Source:
    """
    A source used to generate the narrative.
    Tracks where information came from for transparency.
    """
    text: str
    source_type: SourceType
    reference: Optional[str] = None  # Document ID or citation
    relevance_score: Optional[float] = None

    def is_verified(self) -> bool:
        """Check if this is a verified source."""
        return self.source_type == SourceType.VERAZ

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "text": self.text,
            "source_type": self.source_type.value,
            "reference": self.reference,
            "relevance_score": self.relevance_score
        }


@dataclass
class Trazabilidad:
    """
    Traceability information for a narrative.
    Tracks all sources used to generate the narrative.
    """
    sources: List[Source]
    primary_source_type: SourceType
    confidence_score: float  # 0.0 to 1.0

    def __post_init__(self):
        """Validate trazabilidad."""
        if not 0.0 <= self.confidence_score <= 1.0:
            raise ValueError("confidence_score must be between 0.0 and 1.0")

        if not self.sources:
            raise ValueError("At least one source is required")

    def get_verified_sources(self) -> List[Source]:
        """Get all verified sources."""
        return [s for s in self.sources if s.is_verified()]

    def get_plausible_sources(self) -> List[Source]:
        """Get all plausible sources."""
        return [s for s in self.sources if not s.is_verified()]

    def has_verified_sources(self) -> bool:
        """Check if there are any verified sources."""
        return len(self.get_verified_sources()) > 0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "sources": [s.to_dict() for s in self.sources],
            "primary_source_type": self.primary_source_type.value,
            "confidence_score": self.confidence_score,
            "verified_sources_count": len(self.get_verified_sources()),
            "plausible_sources_count": len(self.get_plausible_sources())
        }
