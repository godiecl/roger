"""
Remove member use case for ROGER - Valeria API.
"""

from app.features.manage_projects.domain.project_port import IProjectRepository
from app.features.manage_projects.domain.project_role import ProjectRole
from app.shared.domain.exceptions import (
    EntityNotFoundError,
    PermissionDeniedError,
    BusinessRuleViolationError
)


class RemoveMemberUseCase:
    """Use case for removing a member from a project."""

    def __init__(self, project_repository: IProjectRepository):
        self.project_repository = project_repository

    async def execute(
        self,
        project_id: int,
        user_id: int,
        requesting_user_id: int
    ) -> bool:
        """
        Remove a member from a project. Only LIDER can remove members.
        The owner cannot be removed.

        Args:
            project_id: ID of the project.
            user_id: ID of the user to remove.
            requesting_user_id: ID of the user making the request.

        Returns:
            True if removed.

        Raises:
            EntityNotFoundError: If project not found.
            PermissionDeniedError: If requester cannot manage members.
            BusinessRuleViolationError: If trying to remove the owner.
        """
        project = await self.project_repository.get_by_id(project_id)
        if not project:
            raise EntityNotFoundError("Project", project_id)

        # Cannot remove the project owner
        if project.is_owner(user_id):
            raise BusinessRuleViolationError(
                "Cannot remove the project owner from the project"
            )

        # Check permission
        requester_member = await self.project_repository.get_member(
            project_id, requesting_user_id
        )
        if not project.is_owner(requesting_user_id) and (
            not requester_member
            or not ProjectRole.can_manage_members(requester_member.role)
        ):
            raise PermissionDeniedError(
                "Only the project leader can manage members"
            )

        # Verify the target is actually a member
        target_member = await self.project_repository.get_member(
            project_id, user_id
        )
        if not target_member:
            raise EntityNotFoundError("ProjectMember", user_id)

        return await self.project_repository.remove_member(project_id, user_id)
