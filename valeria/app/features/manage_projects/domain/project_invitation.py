"""
ProjectInvitation domain entity for ROGER - Valeria API.
"""

from datetime import datetime
from typing import Optional

from app.shared.domain.base_entity import BaseEntity


class InvitationStatus:
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    DECLINED = 'declined'


class ProjectInvitation(BaseEntity):
    """
    ProjectInvitation domain entity.
    Represents a pending invitation for a user to join a project.
    """

    def __init__(
        self,
        project_id: int,
        invited_user_id: int,
        invited_by_user_id: int,
        status: str = InvitationStatus.PENDING,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        super().__init__(id, created_at, updated_at)
        self.project_id = project_id
        self.invited_user_id = invited_user_id
        self.invited_by_user_id = invited_by_user_id
        self.status = status

    def accept(self) -> None:
        self.status = InvitationStatus.ACCEPTED
        self.updated_at = datetime.utcnow()

    def decline(self) -> None:
        self.status = InvitationStatus.DECLINED
        self.updated_at = datetime.utcnow()

    def is_pending(self) -> bool:
        return self.status == InvitationStatus.PENDING

    def __repr__(self) -> str:
        return (
            f"ProjectInvitation(id={self.id}, project_id={self.project_id}, "
            f"invited_user_id={self.invited_user_id}, status={self.status})"
        )
