"""
Add member use case for ROGER - Valeria API.
"""

from app.features.manage_projects.domain.project import ProjectMember
from app.features.manage_projects.domain.project_port import IProjectRepository
from app.features.manage_projects.domain.project_role import ProjectRole
from app.shared.domain.exceptions import (
    EntityNotFoundError,
    PermissionDeniedError,
    BusinessRuleViolationError
)


class AddMemberUseCase:
    """Use case for adding a member to a project."""

    def __init__(self, project_repository: IProjectRepository):
        self.project_repository = project_repository

    async def execute(
        self,
        project_id: int,
        user_id: int,
        role: ProjectRole,
        requesting_user_id: int
    ) -> ProjectMember:
        """
        Add a member to a project. Only LIDER can manage members.

        Args:
            project_id: ID of the project.
            user_id: ID of the user to add.
            role: Role to assign.
            requesting_user_id: ID of the user making the request.

        Returns:
            Created ProjectMember.

        Raises:
            EntityNotFoundError: If project not found.
            PermissionDeniedError: If requester cannot manage members.
            BusinessRuleViolationError: If user is already a member.
        """
        # Verify project exists
        project = await self.project_repository.get_by_id(project_id)
        if not project:
            raise EntityNotFoundError("Project", project_id)

        # Check permission: only owner or LIDER can add members
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

        # Check if user is already a member
        existing = await self.project_repository.get_member(project_id, user_id)
        if existing:
            raise BusinessRuleViolationError(
                f"User {user_id} is already a member of project {project_id}"
            )

        member = ProjectMember(
            project_id=project_id,
            user_id=user_id,
            role=role
        )

        return await self.project_repository.add_member(member)
