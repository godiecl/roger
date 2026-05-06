"""
Create invitation use case for ROGER - Valeria API.
"""

from app.features.manage_projects.domain.project_invitation import ProjectInvitation
from app.features.manage_projects.domain.project_port import IProjectRepository
from app.features.manage_projects.domain.project_role import ProjectRole
from app.features.manage_projects.infrastructure.adapters.project_invitation_repository import ProjectInvitationRepository
from app.shared.domain.exceptions import (
    EntityNotFoundError,
    PermissionDeniedError,
    BusinessRuleViolationError
)


class CreateInvitationUseCase:

    def __init__(
        self,
        project_repository: IProjectRepository,
        invitation_repository: ProjectInvitationRepository
    ):
        self.project_repository = project_repository
        self.invitation_repository = invitation_repository

    async def execute(
        self,
        project_id: int,
        invited_user_id: int,
        requesting_user_id: int
    ) -> ProjectInvitation:
        # Verify project exists
        project = await self.project_repository.get_by_id(project_id)
        if not project:
            raise EntityNotFoundError("Project", project_id)

        # Check permission: only owner or LIDER can invite
        requester_member = await self.project_repository.get_member(project_id, requesting_user_id)
        if not project.is_owner(requesting_user_id) and (
            not requester_member
            or not ProjectRole.can_manage_members(requester_member.role)
        ):
            raise PermissionDeniedError("Only the project leader can invite members")

        # Cannot invite yourself
        if invited_user_id == requesting_user_id:
            raise BusinessRuleViolationError("Cannot invite yourself")

        # Check user is not already a member
        existing_member = await self.project_repository.get_member(project_id, invited_user_id)
        if existing_member:
            raise BusinessRuleViolationError(
                f"User {invited_user_id} is already a member of this project"
            )

        # Check there's no pending invitation already
        existing_invitation = await self.invitation_repository.get_pending_by_project_and_user(
            project_id, invited_user_id
        )
        if existing_invitation:
            raise BusinessRuleViolationError("There is already a pending invitation for this user")

        # Remove any stale non-pending invitation (e.g. accepted from a previously removed member)
        # so the unique constraint doesn't block re-inviting
        await self.invitation_repository.delete_by_project_and_user(project_id, invited_user_id)

        invitation = ProjectInvitation(
            project_id=project_id,
            invited_user_id=invited_user_id,
            invited_by_user_id=requesting_user_id
        )
        return await self.invitation_repository.create(invitation)
