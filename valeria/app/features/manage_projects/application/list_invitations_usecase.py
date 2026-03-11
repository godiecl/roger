"""
List invitations use case for ROGER - Valeria API.
"""

from app.features.manage_projects.domain.project_invitation import ProjectInvitation
from app.features.manage_projects.infrastructure.adapters.project_invitation_repository import ProjectInvitationRepository


class ListInvitationsUseCase:

    def __init__(self, invitation_repository: ProjectInvitationRepository):
        self.invitation_repository = invitation_repository

    async def execute(self, user_id: int) -> list[ProjectInvitation]:
        return await self.invitation_repository.list_pending_by_user(user_id)
