"""
Contribution domain entities and field validation for ROGER - Valeria API.
"""

from datetime import datetime
from enum import Enum
from typing import Optional


class ContributionAttributeType(str, Enum):
    CHRONOLOGY = "chronology"
    GEOGRAPHIC = "geographic"
    ENVIRONMENTAL = "environmental"
    TAG = "tag"


class ContributionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


# Valid field names per attribute type.
# Used to validate contributions at submit time.
ALLOWED_FIELDS: dict[str, set[str]] = {
    ContributionAttributeType.CHRONOLOGY: {
        "date_type", "precise_date", "date_from", "date_to",
        "date_hypothesis", "verification_source", "methodology",
        "visual_evidence_notes",
    },
    ContributionAttributeType.GEOGRAPHIC: {
        "location_type", "geographic_location", "latitude", "longitude",
        "location_radius_km", "signage_found", "architectural_landmarks",
        "landscape_features",
    },
    ContributionAttributeType.ENVIRONMENTAL: {
        "setting_type", "specific_typology", "conservation_state",
        "human_env_relationship",
    },
    ContributionAttributeType.TAG: {
        "tag_name", "tag_category",
    },
}


class Contribution:

    def __init__(
        self,
        photograph_id: int,
        contributor_id: int,
        attribute_type: ContributionAttributeType,
        field_name: str,
        proposed_value: str,
        evidence_notes: Optional[str] = None,
        status: ContributionStatus = ContributionStatus.PENDING,
        reviewed_by: Optional[int] = None,
        reviewed_at: Optional[datetime] = None,
        rejection_reason: Optional[str] = None,
        created_at: Optional[datetime] = None,
        id: Optional[int] = None,
    ):
        self.id = id
        self.photograph_id = photograph_id
        self.contributor_id = contributor_id
        self.attribute_type = attribute_type
        self.field_name = field_name
        self.proposed_value = proposed_value
        self.evidence_notes = evidence_notes
        self.status = status
        self.reviewed_by = reviewed_by
        self.reviewed_at = reviewed_at
        self.rejection_reason = rejection_reason
        self.created_at = created_at or datetime.utcnow()

    def is_pending(self) -> bool:
        return self.status == ContributionStatus.PENDING

    def __repr__(self) -> str:
        return (
            f"Contribution(id={self.id}, photograph_id={self.photograph_id}, "
            f"attribute_type={self.attribute_type}, field={self.field_name}, status={self.status})"
        )
