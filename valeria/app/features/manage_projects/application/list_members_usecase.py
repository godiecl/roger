"""
List members use case for ROGER - Valeria API.
"""

from typing import List

from app.features.manage_projects.domain.project import ProjectMember
from app.features.manage_projects.domain.project_port import IProjectRepository
from app.shared.domain.exceptions import EntityNotFoundError, PermissionDeniedError


class ListMembersUseCase:
    """Use case for listing members of a project."""

    def __init__(self, project_repository: IProjectRepository):
        self.project_repository = project_repository

    async def execute(
        self,
        project_id: int,
        requesting_user_id: int
    ) -> List[ProjectMember]:
        """
        List all members of a project. Only members can see the member list.

        Args:
            project_id: ID of the project.
            requesting_user_id: ID of the requesting user.

        Returns:
            List of ProjectMember entities.

        Raises:
            EntityNotFoundError: If project not found.
            PermissionDeniedError: If user is not a member.
        """
        project = await self.project_repository.get_by_id(project_id)
        if not project:
            raise EntityNotFoundError("Project", project_id)

        # Check that the requesting user is a member
        member = await self.project_repository.get_member(
            project_id, requesting_user_id
        )
        if not project.is_owner(requesting_user_id) and not member:
            raise PermissionDeniedError(
                "User is not a member of this project"
            )

        return await self.project_repository.list_members(project_id)
