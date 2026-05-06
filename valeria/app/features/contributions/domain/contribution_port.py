from abc import ABC, abstractmethod
from typing import List, Optional

from app.features.contributions.domain.contribution import Contribution, ContributionAttributeType, ContributionStatus


class IContributionRepository(ABC):

    @abstractmethod
    async def create(self, contribution: Contribution) -> Contribution:
        pass

    @abstractmethod
    async def get_by_id(self, contribution_id: int) -> Optional[Contribution]:
        pass

    @abstractmethod
    async def list_by_photograph(
        self,
        photograph_id: int,
        attribute_type: Optional[ContributionAttributeType] = None,
        status: Optional[ContributionStatus] = None,
    ) -> List[Contribution]:
        pass

    @abstractmethod
    async def list_by_contributor(
        self,
        contributor_id: int,
        status: Optional[ContributionStatus] = None,
    ) -> List[Contribution]:
        pass

    @abstractmethod
    async def list_pending(self, skip: int = 0, limit: int = 50) -> List[Contribution]:
        """List all PENDING contributions — used by curators."""
        pass

    @abstractmethod
    async def update_status(
        self,
        contribution_id: int,
        status: ContributionStatus,
        reviewed_by: int,
        rejection_reason: Optional[str] = None,
    ) -> Contribution:
        pass
