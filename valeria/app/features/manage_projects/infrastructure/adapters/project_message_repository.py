"""
Project message repository implementation.
"""

from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.features.manage_projects.domain.project_message import (
    ProjectMessage,
    IProjectMessageRepository
)
from app.features.manage_projects.infrastructure.persistence.project_message_model import (
    ProjectMessageModel
)


class ProjectMessageRepository(IProjectMessageRepository):
    """SQLAlchemy implementation of IProjectMessageRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, message: ProjectMessage) -> ProjectMessage:
        model = ProjectMessageModel(
            project_id=message.project_id,
            user_id=message.user_id,
            content=message.content,
            message_type=message.message_type,
            sender_name=message.sender_name
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def list_by_project(
        self, project_id: int, skip: int = 0, limit: int = 100
    ) -> List[ProjectMessage]:
        result = await self.session.execute(
            select(ProjectMessageModel)
            .where(ProjectMessageModel.project_id == project_id)
            .order_by(ProjectMessageModel.created_at.asc())
            .offset(skip)
            .limit(limit)
        )
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def count_by_project(self, project_id: int) -> int:
        from sqlalchemy import func
        result = await self.session.execute(
            select(func.count()).where(
                ProjectMessageModel.project_id == project_id
            )
        )
        return result.scalar_one()

    def _to_entity(self, model: ProjectMessageModel) -> ProjectMessage:
        return ProjectMessage(
            id=model.id,
            project_id=model.project_id,
            user_id=model.user_id,
            content=model.content,
            message_type=model.message_type,
            sender_name=model.sender_name,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
