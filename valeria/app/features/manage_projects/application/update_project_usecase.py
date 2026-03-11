"""
Update project use case for ROGER - Valeria API.
"""

from typing import Optional
from datetime import date

from app.features.manage_projects.domain.project import Project
from app.features.manage_projects.domain.project_port import IProjectRepository
from app.features.manage_projects.domain.project_role import ProjectRole
from app.shared.domain.exceptions import (
    EntityNotFoundError,
    PermissionDeniedError,
    ValidationError
)


class UpdateProjectUseCase:
    """Use case for updating a project."""

    def __init__(self, project_repository: IProjectRepository):
        self.project_repository = project_repository

    async def execute(
        self,
        project_id: int,
        user_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        is_active: Optional[bool] = None
    ) -> Project:
        """
        Update a project. Only owner or LIDER/INVESTIGADOR members can update.

        Args:
            project_id: ID of the project to update.
            user_id: ID of the requesting user.
            name: New name (optional).
            description: New description (optional).
            start_date: New start date (optional).
            end_date: New end date (optional).
            is_active: New active status (optional).

        Returns:
            Updated Project.

        Raises:
            EntityNotFoundError: If project not found.
            PermissionDeniedError: If user cannot edit.
            ValidationError: If validation fails.
        """
        project = await self.project_repository.get_by_id(project_id)
        if not project:
            raise EntityNotFoundError("Project", project_id)

        # Check permissions: owner or member with edit rights
        member = await self.project_repository.get_member(project_id, user_id)
        if not project.is_owner(user_id) and (
            not member or not ProjectRole.can_edit_project(member.role)
        ):
            raise PermissionDeniedError(
                "User does not have permission to edit this project"
            )

        # Apply updates
        if name is not None:
            project.name = name
        if description is not None:
            project.description = description
        if start_date is not None:
            project.start_date = start_date
        if end_date is not None:
            project.end_date = end_date
        if is_active is not None:
            project.is_active = is_active

        try:
            project.validate()
        except ValueError as e:
            raise ValidationError(str(e))

        return await self.project_repository.update(project)
