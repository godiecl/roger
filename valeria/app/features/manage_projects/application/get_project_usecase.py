"""
Get project use case for ROGER - Valeria API.
"""

from app.features.manage_projects.domain.project import Project
from app.features.manage_projects.domain.project_port import IProjectRepository
from app.shared.domain.exceptions import EntityNotFoundError, PermissionDeniedError


class GetProjectUseCase:
    """Use case for getting a single project."""

    def __init__(self, project_repository: IProjectRepository):
        self.project_repository = project_repository

    async def execute(self, project_id: int, user_id: int) -> Project:
        """
        Get a project by ID, verifying the user has access.

        Args:
            project_id: ID of the project.
            user_id: ID of the requesting user.

        Returns:
            Project entity.

        Raises:
            EntityNotFoundError: If project not found.
            PermissionDeniedError: If user is not a member.
        """
        project = await self.project_repository.get_by_id(project_id)
        if not project:
            raise EntityNotFoundError("Project", project_id)

        # Check if user is owner or member
        member = await self.project_repository.get_member(project_id, user_id)
        if not project.is_owner(user_id) and not member:
            raise PermissionDeniedError("User is not a member of this project")

        return project
