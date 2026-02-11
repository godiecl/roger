"""
Narrative domain entity
"""
from typing import Optional, List
from datetime import datetime

from app.features.generate_narrative.domain.trazabilidad import Trazabilidad, SourceType
from app.shared.domain.base_entity import BaseEntity


class Narrative(BaseEntity):
    """
    Domain entity representing a generated narrative about an image.
    """

    def __init__(
        self,
        image_id: int,
        text: str,
        trazabilidad: Trazabilidad,
        user_id: Optional[int] = None,
        prompt: Optional[str] = None,
        language: str = "es",
        model_used: Optional[str] = None,
        generation_time_ms: Optional[int] = None,
        is_approved: bool = False,
        approved_by: Optional[int] = None,
        approved_at: Optional[datetime] = None,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """
        Initialize a Narrative.

        Args:
            image_id: ID of the image this narrative describes
            text: The generated narrative text
            trazabilidad: Traceability information with sources
            user_id: ID of user who requested the narrative
            prompt: Original prompt used for generation
            language: Language of the narrative (default: Spanish)
            model_used: AI model used for generation
            generation_time_ms: Time taken to generate (milliseconds)
            is_approved: Whether narrative is approved by curator
            approved_by: ID of user who approved
            approved_at: When it was approved
            id: Entity ID
            created_at: Creation timestamp
            updated_at: Last update timestamp
        """
        super().__init__(id, created_at, updated_at)
        self.image_id = image_id
        self.text = text
        self.trazabilidad = trazabilidad
        self.user_id = user_id
        self.prompt = prompt
        self.language = language
        self.model_used = model_used
        self.generation_time_ms = generation_time_ms
        self.is_approved = is_approved
        self.approved_by = approved_by
        self.approved_at = approved_at

        self.validate()

    def validate(self):
        """Validate narrative business rules."""
        if not self.text or len(self.text.strip()) == 0:
            raise ValueError("Narrative text cannot be empty")

        if len(self.text) > 10000:
            raise ValueError("Narrative text cannot exceed 10000 characters")

        if self.language not in ["es", "en", "de"]:
            raise ValueError("Language must be 'es', 'en', or 'de'")

        if self.is_approved and not self.approved_by:
            raise ValueError("approved_by must be set when is_approved is True")

    def approve(self, approved_by: int):
        """
        Approve this narrative.

        Args:
            approved_by: ID of the user approving
        """
        self.is_approved = True
        self.approved_by = approved_by
        self.approved_at = datetime.utcnow()

    def unapprove(self):
        """Unapprove this narrative."""
        self.is_approved = False
        self.approved_by = None
        self.approved_at = None

    def is_verified(self) -> bool:
        """Check if narrative is based on verified sources."""
        return self.trazabilidad.primary_source_type == SourceType.VERAZ

    def is_plausible(self) -> bool:
        """Check if narrative is based on plausible sources."""
        return self.trazabilidad.primary_source_type == SourceType.VEROSIMIL

    def get_confidence_level(self) -> str:
        """Get human-readable confidence level."""
        score = self.trazabilidad.confidence_score
        if score >= 0.8:
            return "high"
        elif score >= 0.5:
            return "medium"
        else:
            return "low"

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "image_id": self.image_id,
            "text": self.text,
            "trazabilidad": self.trazabilidad.to_dict(),
            "user_id": self.user_id,
            "prompt": self.prompt,
            "language": self.language,
            "model_used": self.model_used,
            "generation_time_ms": self.generation_time_ms,
            "is_approved": self.is_approved,
            "approved_by": self.approved_by,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "is_verified": self.is_verified(),
            "confidence_level": self.get_confidence_level(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
