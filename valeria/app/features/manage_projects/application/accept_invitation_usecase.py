"""
Accept invitation use case for ROGER - Valeria API.
"""

from app.features.manage_projects.domain.project import ProjectMember
from app.features.manage_projects.domain.project_invitation import ProjectInvitation
from app.features.manage_projects.domain.project_role import ProjectRole
from app.features.manage_projects.domain.project_port import IProjectRepository
from app.features.manage_projects.infrastructure.adapters.project_invitation_repository import ProjectInvitationRepository
from app.shared.domain.exceptions import EntityNotFoundError, PermissionDeniedError, BusinessRuleViolationError


class AcceptInvitationUseCase:

    def __init__(
        self,
        project_repository: IProjectRepository,
        invitation_repository: ProjectInvitationRepository
    ):
        self.project_repository = project_repository
        self.invitation_repository = invitation_repository

    async def execute(self, invitation_id: int, requesting_user_id: int) -> ProjectMember:
        invitation = await self.invitation_repository.get_by_id(invitation_id)
        if not invitation:
            raise EntityNotFoundError("Invitation", invitation_id)

        if invitation.invited_user_id != requesting_user_id:
            raise PermissionDeniedError("You can only accept your own invitations")

        if not invitation.is_pending():
            raise BusinessRuleViolationError("This invitation is no longer pending")

        invitation.accept()
        await self.invitation_repository.update_status(invitation)

        member = ProjectMember(
            project_id=invitation.project_id,
            user_id=invitation.invited_user_id,
            role=ProjectRole.OBSERVADOR
        )
        return await self.project_repository.add_member(member)
