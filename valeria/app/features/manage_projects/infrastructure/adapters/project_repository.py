"""
Project repository implementation for ROGER - Valeria API.
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, func

from app.features.manage_projects.domain.project import Project, ProjectMember
from app.features.manage_projects.domain.project_port import IProjectRepository
from app.features.manage_projects.infrastructure.persistence.project_model import (
    ProjectModel,
    ProjectMemberModel
)


class ProjectRepository(IProjectRepository):
    """SQLAlchemy implementation of project repository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # --- Project CRUD ---

    async def create(self, project: Project) -> Project:
        """Create a new project."""
        project_model = ProjectModel(
            name=project.name,
            description=project.description,
            start_date=project.start_date,
            end_date=project.end_date,
            owner_id=project.owner_id,
            is_active=project.is_active
        )

        self.session.add(project_model)
        await self.session.flush()
        await self.session.refresh(project_model)

        return self._to_entity(project_model)

    async def get_by_id(self, project_id: int) -> Optional[Project]:
        """Get project by ID."""
        result = await self.session.execute(
            select(ProjectModel).where(ProjectModel.id == project_id)
        )
        project_model = result.scalar_one_or_none()

        return self._to_entity(project_model) if project_model else None

    async def list_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Project]:
        """List projects where user is owner or member."""
        member_subquery = (
            select(ProjectMemberModel.project_id)
            .where(ProjectMemberModel.user_id == user_id)
        )

        query = (
            select(ProjectModel)
            .where(
                or_(
                    ProjectModel.owner_id == user_id,
                    ProjectModel.id.in_(member_subquery)
                )
            )
            .offset(skip)
            .limit(limit)
            .order_by(ProjectModel.created_at.desc())
        )

        result = await self.session.execute(query)
        project_models = result.scalars().all()

        return [self._to_entity(model) for model in project_models]

    async def count_owned_by_user(self, user_id: int) -> int:
        """Count projects owned by a user."""
        result = await self.session.execute(
            select(func.count()).where(ProjectModel.owner_id == user_id)
        )
        return result.scalar_one()

    async def update(self, project: Project) -> Project:
        """Update an existing project."""
        result = await self.session.execute(
            select(ProjectModel).where(ProjectModel.id == project.id)
        )
        project_model = result.scalar_one_or_none()

        if not project_model:
            raise ValueError(f"Project with id {project.id} not found")

        project_model.name = project.name
        project_model.description = project.description
        project_model.start_date = project.start_date
        project_model.end_date = project.end_date
        project_model.owner_id = project.owner_id
        project_model.is_active = project.is_active

        await self.session.flush()
        await self.session.refresh(project_model)

        return self._to_entity(project_model)

    async def delete(self, project_id: int) -> bool:
        """Delete a project (cascade deletes members)."""
        result = await self.session.execute(
            select(ProjectModel).where(ProjectModel.id == project_id)
        )
        project_model = result.scalar_one_or_none()

        if project_model:
            await self.session.delete(project_model)
            return True
        return False

    # --- Member management ---

    async def add_member(self, member: ProjectMember) -> ProjectMember:
        """Add a member to a project."""
        member_model = ProjectMemberModel(
            project_id=member.project_id,
            user_id=member.user_id,
            role=member.role
        )

        self.session.add(member_model)
        await self.session.flush()
        await self.session.refresh(member_model)

        return self._to_member_entity(member_model)

    async def remove_member(self, project_id: int, user_id: int) -> bool:
        """Remove a member from a project."""
        result = await self.session.execute(
            select(ProjectMemberModel).where(
                ProjectMemberModel.project_id == project_id,
                ProjectMemberModel.user_id == user_id
            )
        )
        member_model = result.scalar_one_or_none()

        if member_model:
            await self.session.delete(member_model)
            return True
        return False

    async def get_member(
        self,
        project_id: int,
        user_id: int
    ) -> Optional[ProjectMember]:
        """Get a specific member of a project."""
        result = await self.session.execute(
            select(ProjectMemberModel).where(
                ProjectMemberModel.project_id == project_id,
                ProjectMemberModel.user_id == user_id
            )
        )
        member_model = result.scalar_one_or_none()

        return self._to_member_entity(member_model) if member_model else None

    async def list_members(self, project_id: int) -> List[ProjectMember]:
        """List all members of a project."""
        result = await self.session.execute(
            select(ProjectMemberModel)
            .where(ProjectMemberModel.project_id == project_id)
            .order_by(ProjectMemberModel.created_at.asc())
        )
        member_models = result.scalars().all()

        return [self._to_member_entity(model) for model in member_models]

    # --- Conversion methods ---

    def _to_entity(self, model: ProjectModel) -> Project:
        """Convert SQLAlchemy project model to domain entity."""
        return Project(
            id=model.id,
            name=model.name,
            description=model.description,
            start_date=model.start_date,
            end_date=model.end_date,
            owner_id=model.owner_id,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def _to_member_entity(self, model: ProjectMemberModel) -> ProjectMember:
        """Convert SQLAlchemy member model to domain entity."""
        return ProjectMember(
            id=model.id,
            project_id=model.project_id,
            user_id=model.user_id,
            role=model.role,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
