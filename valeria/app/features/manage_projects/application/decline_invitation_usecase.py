"""
Decline invitation use case for ROGER - Valeria API.
"""

from app.features.manage_projects.domain.project_invitation import ProjectInvitation
from app.features.manage_projects.infrastructure.adapters.project_invitation_repository import ProjectInvitationRepository
from app.shared.domain.exceptions import EntityNotFoundError, PermissionDeniedError, BusinessRuleViolationError


class DeclineInvitationUseCase:

    def __init__(self, invitation_repository: ProjectInvitationRepository):
        self.invitation_repository = invitation_repository

    async def execute(self, invitation_id: int, requesting_user_id: int) -> ProjectInvitation:
        invitation = await self.invitation_repository.get_by_id(invitation_id)
        if not invitation:
            raise EntityNotFoundError("Invitation", invitation_id)

        if invitation.invited_user_id != requesting_user_id:
            raise PermissionDeniedError("You can only decline your own invitations")

        if not invitation.is_pending():
            raise BusinessRuleViolationError("This invitation is no longer pending")

        invitation.decline()
        return await self.invitation_repository.update_status(invitation)
