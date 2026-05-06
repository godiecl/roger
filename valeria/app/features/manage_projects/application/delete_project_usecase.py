"""
Delete project use case for ROGER - Valeria API.
"""

from app.features.manage_projects.domain.project_port import IProjectRepository
from app.shared.domain.exceptions import EntityNotFoundError, PermissionDeniedError


class DeleteProjectUseCase:
    """Use case for deleting a project."""

    def __init__(self, project_repository: IProjectRepository):
        self.project_repository = project_repository

    async def execute(self, project_id: int, user_id: int) -> bool:
        """
        Delete a project. Only the owner can delete.

        Args:
            project_id: ID of the project to delete.
            user_id: ID of the requesting user.

        Returns:
            True if deleted.

        Raises:
            EntityNotFoundError: If project not found.
            PermissionDeniedError: If user is not the owner.
        """
        project = await self.project_repository.get_by_id(project_id)
        if not project:
            raise EntityNotFoundError("Project", project_id)

        if not project.is_owner(user_id):
            raise PermissionDeniedError("Only the project owner can delete it")

        return await self.project_repository.delete(project_id)
