"""
ProjectInvitation repository implementation for ROGER - Valeria API.
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.features.manage_projects.domain.project_invitation import ProjectInvitation, InvitationStatus
from app.features.manage_projects.infrastructure.persistence.project_invitation_model import ProjectInvitationModel


class ProjectInvitationRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, invitation: ProjectInvitation) -> ProjectInvitation:
        model = ProjectInvitationModel(
            project_id=invitation.project_id,
            invited_user_id=invitation.invited_user_id,
            invited_by_user_id=invitation.invited_by_user_id,
            status=invitation.status
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, invitation_id: int) -> Optional[ProjectInvitation]:
        result = await self.session.execute(
            select(ProjectInvitationModel).where(ProjectInvitationModel.id == invitation_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_pending_by_project_and_user(
        self, project_id: int, user_id: int
    ) -> Optional[ProjectInvitation]:
        result = await self.session.execute(
            select(ProjectInvitationModel).where(
                ProjectInvitationModel.project_id == project_id,
                ProjectInvitationModel.invited_user_id == user_id,
                ProjectInvitationModel.status == InvitationStatus.PENDING
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_by_project(self, project_id: int) -> list[ProjectInvitation]:
        """List all invitations for a project (any status)."""
        result = await self.session.execute(
            select(ProjectInvitationModel)
            .where(ProjectInvitationModel.project_id == project_id)
            .order_by(ProjectInvitationModel.created_at.desc())
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_pending_by_user(self, user_id: int) -> list[ProjectInvitation]:
        result = await self.session.execute(
            select(ProjectInvitationModel).where(
                ProjectInvitationModel.invited_user_id == user_id,
                ProjectInvitationModel.status == InvitationStatus.PENDING
            )
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def update_status(self, invitation: ProjectInvitation) -> ProjectInvitation:
        result = await self.session.execute(
            select(ProjectInvitationModel).where(ProjectInvitationModel.id == invitation.id)
        )
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"Invitation {invitation.id} not found")
        model.status = invitation.status
        model.updated_at = invitation.updated_at
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    def _to_entity(self, model: ProjectInvitationModel) -> ProjectInvitation:
        return ProjectInvitation(
            id=model.id,
            project_id=model.project_id,
            invited_user_id=model.invited_user_id,
            invited_by_user_id=model.invited_by_user_id,
            status=model.status,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
