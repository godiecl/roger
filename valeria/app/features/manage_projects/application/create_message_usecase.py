"""
Create user message use case.
"""

from app.features.manage_projects.domain.project_message import (
    ProjectMessage,
    IProjectMessageRepository
)
from app.features.manage_projects.domain.project_port import IProjectRepository
from app.shared.domain.exceptions import EntityNotFoundError, PermissionDeniedError


class CreateMessageUseCase:
    """Use case for creating a user message in a project chat."""

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
        content: str,
        sender_name: str
    ) -> ProjectMessage:
        """
        Create a user message in the project chat.

        Args:
            project_id: ID of the project.
            user_id: ID of the user sending the message.
            content: Message content.
            sender_name: Display name of the sender.

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
                "Only project members can send messages"
            )

        message = ProjectMessage(
            project_id=project_id,
            user_id=user_id,
            content=content.strip(),
            message_type='user',
            sender_name=sender_name
        )

        return await self.message_repository.create(message)
