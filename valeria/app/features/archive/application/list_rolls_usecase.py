from typing import List
from app.features.archive.domain.archive import Roll
from app.features.archive.domain.archive_port import IArchiveRepository


class ListRollsUseCase:
    def __init__(self, repository: IArchiveRepository):
        self.repository = repository

    async def execute(self, box_id: int, skip: int = 0, limit: int = 100) -> List[Roll]:
        return await self.repository.list_rolls(box_id, skip, limit)
