"""
Project domain entities for ROGER - Valeria API.
"""

from datetime import datetime, date
from typing import Optional

from app.shared.domain.base_entity import BaseEntity
from app.features.manage_projects.domain.project_role import ProjectRole


class Project(BaseEntity):
    """
    Project domain entity.
    Represents a research collaboration group (RF-10).
    """

    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        owner_id: Optional[int] = None,
        is_active: bool = True,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        super().__init__(id, created_at, updated_at)
        self.name = name
        self.description = description
        self.start_date = start_date
        self.end_date = end_date
        self.owner_id = owner_id
        self.is_active = is_active

        self.validate()

    def validate(self):
        """Validate project business rules."""
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Project name cannot be empty")
        if len(self.name) > 255:
            raise ValueError("Project name cannot exceed 255 characters")
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("End date cannot be before start date")

    def activate(self) -> None:
        """Activate the project."""
        self.is_active = True
        self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        """Deactivate the project."""
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def is_owner(self, user_id: int) -> bool:
        """Check if a user is the project owner."""
        return self.owner_id == user_id

    def __repr__(self) -> str:
        return f"Project(id={self.id}, name={self.name}, owner_id={self.owner_id})"


class ProjectMember(BaseEntity):
    """
    ProjectMember domain entity.
    Represents a user's membership and role within a project.
    """

    def __init__(
        self,
        project_id: int,
        user_id: int,
        role: ProjectRole = ProjectRole.OBSERVADOR,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        super().__init__(id, created_at, updated_at)
        self.project_id = project_id
        self.user_id = user_id
        self.role = role

    def can_manage_members(self) -> bool:
        """Check if this member can add/remove other members."""
        return ProjectRole.can_manage_members(self.role)

    def can_edit_project(self) -> bool:
        """Check if this member can edit project details."""
        return ProjectRole.can_edit_project(self.role)

    def can_share_content(self) -> bool:
        """Check if this member can share content."""
        return ProjectRole.can_share_content(self.role)

    def change_role(self, new_role: ProjectRole) -> None:
        """Change the member's role."""
        self.role = new_role
        self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        return (
            f"ProjectMember(id={self.id}, project_id={self.project_id}, "
            f"user_id={self.user_id}, role={self.role})"
        )
