"""
ProjectMessage domain entity and port for ROGER - Valeria API.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, List

from app.shared.domain.base_entity import BaseEntity


class ProjectMessage(BaseEntity):
    """
    ProjectMessage domain entity.
    Represents a chat message within a project (user or AI).
    """

    def __init__(
        self,
        project_id: int,
        user_id: int,
        content: str,
        message_type: str = 'user',
        sender_name: Optional[str] = None,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        super().__init__(id, created_at, updated_at)
        self.project_id = project_id
        self.user_id = user_id
        self.content = content
        self.message_type = message_type  # 'user' or 'ai'
        self.sender_name = sender_name

        self._validate()

    def _validate(self):
        if not self.content or not self.content.strip():
            raise ValueError("Message content cannot be empty")
        if self.message_type not in ('user', 'ai'):
            raise ValueError("message_type must be 'user' or 'ai'")

    def __repr__(self) -> str:
        return (
            f"ProjectMessage(id={self.id}, project_id={self.project_id}, "
            f"user_id={self.user_id}, type={self.message_type})"
        )


class IProjectMessageRepository(ABC):
    """Port (interface) for project message persistence."""

    @abstractmethod
    async def create(self, message: ProjectMessage) -> ProjectMessage:
        """Persist a new message and return it with id/timestamps."""
        ...

    @abstractmethod
    async def list_by_project(
        self, project_id: int, skip: int = 0, limit: int = 100
    ) -> List[ProjectMessage]:
        """List messages for a project ordered by created_at ASC."""
        ...

    @abstractmethod
    async def count_by_project(self, project_id: int) -> int:
        """Count total messages for a project."""
        ...
