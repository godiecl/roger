"""
List messages use case.
"""

from typing import List

from app.features.manage_projects.domain.project_message import (
    ProjectMessage,
    IProjectMessageRepository
)
from app.features.manage_projects.domain.project_port import IProjectRepository
from app.shared.domain.exceptions import EntityNotFoundError, PermissionDeniedError


class ListMessagesUseCase:
    """Use case for listing messages in a project chat."""

    def __init__(
        self,
        project_repository: IProjectRepository,
        message_repository: IProjectMessageRepository
    ):
        self.project_repository = project_repository
        self.message_repository = message_repository

    async def execute(
        self,
        project_id: int,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[ProjectMessage]:
        """
        List messages for a project.

        Raises:
            EntityNotFoundError: If project not found.
            PermissionDeniedError: If user is not a project member.
        """
        project = await self.project_repository.get_by_id(project_id)
        if not project:
            raise EntityNotFoundError("Project", project_id)

        member = await self.project_repository.get_member(project_id, user_id)
        if not member and not project.is_owner(user_id):
            raise PermissionDeniedError(
                "Only project members can view messages"
            )

        return await self.message_repository.list_by_project(project_id, skip, limit)
