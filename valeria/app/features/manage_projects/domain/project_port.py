"""
Project repository port (interface) for ROGER - Valeria API.
"""

from abc import ABC, abstractmethod
from typing import Optional, List

from app.features.manage_projects.domain.project import Project, ProjectMember


class IProjectRepository(ABC):
    """Repository interface for Project aggregate."""

    # --- Project CRUD ---

    @abstractmethod
    async def create(self, project: Project) -> Project:
        """Create a new project."""
        pass

    @abstractmethod
    async def get_by_id(self, project_id: int) -> Optional[Project]:
        """Get project by ID."""
        pass

    @abstractmethod
    async def list_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Project]:
        """List projects where user is owner or member."""
        pass

    @abstractmethod
    async def update(self, project: Project) -> Project:
        """Update an existing project."""
        pass

    @abstractmethod
    async def delete(self, project_id: int) -> bool:
        """Delete a project and all its memberships."""
        pass

    @abstractmethod
    async def count_owned_by_user(self, user_id: int) -> int:
        """Count projects owned (created) by a user."""
        pass

    # --- Member management ---

    @abstractmethod
    async def add_member(self, member: ProjectMember) -> ProjectMember:
        """Add a member to a project."""
        pass

    @abstractmethod
    async def remove_member(self, project_id: int, user_id: int) -> bool:
        """Remove a member from a project."""
        pass

    @abstractmethod
    async def get_member(
        self,
        project_id: int,
        user_id: int
    ) -> Optional[ProjectMember]:
        """Get a specific member of a project."""
        pass

    @abstractmethod
    async def list_members(
        self,
        project_id: int
    ) -> List[ProjectMember]:
        """List all members of a project."""
        pass
