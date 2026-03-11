"""
Create project use case for ROGER - Valeria API.
"""

from app.features.manage_projects.domain.project import Project, ProjectMember
from app.features.manage_projects.domain.project_port import IProjectRepository
from app.features.manage_projects.domain.project_role import ProjectRole
from app.shared.domain.exceptions import ValidationError


class CreateProjectUseCase:
    """Use case for creating a new project."""

    def __init__(self, project_repository: IProjectRepository):
        self.project_repository = project_repository

    async def execute(
        self,
        name: str,
        owner_id: int,
        description: str = None,
        start_date=None,
        end_date=None
    ) -> Project:
        """
        Create a new project and add the owner as LIDER member.

        Args:
            name: Project name.
            owner_id: ID of the user creating the project.
            description: Optional project description.
            start_date: Optional start date.
            end_date: Optional end date.

        Returns:
            Created Project.

        Raises:
            ValidationError: If validation fails.
        """
        try:
            project = Project(
                name=name,
                description=description,
                start_date=start_date,
                end_date=end_date,
                owner_id=owner_id,
                is_active=True
            )
        except ValueError as e:
            raise ValidationError(str(e))

        created_project = await self.project_repository.create(project)

        # Automatically add the owner as LIDER member
        owner_member = ProjectMember(
            project_id=created_project.id,
            user_id=owner_id,
            role=ProjectRole.LIDER
        )
        await self.project_repository.add_member(owner_member)

        return created_project
