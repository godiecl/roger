from typing import Optional

from app.features.contributions.domain.contribution import Contribution, ContributionStatus
from app.features.contributions.domain.contribution_port import IContributionRepository
from app.shared.domain.exceptions import EntityNotFoundError, BusinessRuleViolationError


class RejectContributionUseCase:

    def __init__(self, repository: IContributionRepository):
        self.repository = repository

    async def execute(
        self,
        contribution_id: int,
        reviewer_id: int,
        rejection_reason: Optional[str] = None,
    ) -> Contribution:
        contribution = await self.repository.get_by_id(contribution_id)
        if not contribution:
            raise EntityNotFoundError(f"Contribución {contribution_id} no encontrada.")
        if not contribution.is_pending():
            raise BusinessRuleViolationError(
                f"Solo se pueden rechazar contribuciones PENDING. Estado actual: {contribution.status}"
            )
        return await self.repository.update_status(
            contribution_id=contribution_id,
            status=ContributionStatus.REJECTED,
            reviewed_by=reviewer_id,
            rejection_reason=rejection_reason,
        )
