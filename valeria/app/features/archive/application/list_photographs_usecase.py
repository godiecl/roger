from typing import List
from app.features.archive.domain.archive import Photograph
from app.features.archive.domain.archive_port import IArchiveRepository


class ListPhotographsUseCase:
    def __init__(self, repository: IArchiveRepository):
        self.repository = repository

    async def execute(self, roll_id: int, skip: int = 0, limit: int = 100) -> List[Photograph]:
        return await self.repository.list_photographs(roll_id, skip, limit)
