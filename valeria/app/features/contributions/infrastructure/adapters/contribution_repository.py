from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.features.contributions.domain.contribution import (
    Contribution, ContributionAttributeType, ContributionStatus,
)
from app.features.contributions.domain.contribution_port import IContributionRepository
from app.features.contributions.infrastructure.persistence.contribution_model import (
    MetadataContributionModel,
)


class ContributionRepository(IContributionRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, contribution: Contribution) -> Contribution:
        model = MetadataContributionModel(
            photograph_id=contribution.photograph_id,
            contributor_id=contribution.contributor_id,
            attribute_type=contribution.attribute_type,
            field_name=contribution.field_name,
            proposed_value=contribution.proposed_value,
            evidence_notes=contribution.evidence_notes,
            status=contribution.status,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, contribution_id: int) -> Optional[Contribution]:
        result = await self.session.execute(
            select(MetadataContributionModel).where(MetadataContributionModel.id == contribution_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_by_photograph(
        self,
        photograph_id: int,
        attribute_type: Optional[ContributionAttributeType] = None,
        status: Optional[ContributionStatus] = None,
    ) -> List[Contribution]:
        q = select(MetadataContributionModel).where(
            MetadataContributionModel.photograph_id == photograph_id
        )
        if attribute_type:
            q = q.where(MetadataContributionModel.attribute_type == attribute_type)
        if status:
            q = q.where(MetadataContributionModel.status == status)
        q = q.order_by(MetadataContributionModel.created_at.desc())
        result = await self.session.execute(q)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_by_contributor(
        self,
        contributor_id: int,
        status: Optional[ContributionStatus] = None,
    ) -> List[Contribution]:
        q = select(MetadataContributionModel).where(
            MetadataContributionModel.contributor_id == contributor_id
        )
        if status:
            q = q.where(MetadataContributionModel.status == status)
        q = q.order_by(MetadataContributionModel.created_at.desc())
        result = await self.session.execute(q)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_pending(self, skip: int = 0, limit: int = 50) -> List[Contribution]:
        result = await self.session.execute(
            select(MetadataContributionModel)
            .where(MetadataContributionModel.status == ContributionStatus.PENDING)
            .order_by(MetadataContributionModel.created_at.asc())
            .offset(skip)
            .limit(limit)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def update_status(
        self,
        contribution_id: int,
        status: ContributionStatus,
        reviewed_by: int,
        rejection_reason: Optional[str] = None,
    ) -> Contribution:
        await self.session.execute(
            update(MetadataContributionModel)
            .where(MetadataContributionModel.id == contribution_id)
            .values(
                status=status,
                reviewed_by=reviewed_by,
                reviewed_at=datetime.now(timezone.utc),
                rejection_reason=rejection_reason,
            )
        )
        await self.session.flush()
        result = await self.session.execute(
            select(MetadataContributionModel).where(MetadataContributionModel.id == contribution_id)
        )
        return self._to_entity(result.scalar_one())

    def _to_entity(self, m: MetadataContributionModel) -> Contribution:
        return Contribution(
            id=m.id,
            photograph_id=m.photograph_id,
            contributor_id=m.contributor_id,
            attribute_type=m.attribute_type,
            field_name=m.field_name,
            proposed_value=m.proposed_value,
            evidence_notes=m.evidence_notes,
            status=m.status,
            reviewed_by=m.reviewed_by,
            reviewed_at=m.reviewed_at,
            rejection_reason=m.rejection_reason,
            created_at=m.created_at,
        )
