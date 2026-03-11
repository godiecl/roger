"""
List projects use case for ROGER - Valeria API.
"""

from typing import List

from app.features.manage_projects.domain.project import Project
from app.features.manage_projects.domain.project_port import IProjectRepository


class ListProjectsUseCase:
    """Use case for listing a user's projects."""

    def __init__(self, project_repository: IProjectRepository):
        self.project_repository = project_repository

    async def execute(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Project]:
        """
        List projects where the user is owner or member.

        Args:
            user_id: ID of the user.
            skip: Pagination offset.
            limit: Pagination limit.

        Returns:
            List of projects.
        """
        return await self.project_repository.list_by_user(
            user_id=user_id,
            skip=skip,
            limit=limit
        )
