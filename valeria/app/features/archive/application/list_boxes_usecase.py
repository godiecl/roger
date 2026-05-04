from typing import List
from app.features.archive.domain.archive import Box
from app.features.archive.domain.archive_port import IArchiveRepository


class ListBoxesUseCase:
    def __init__(self, repository: IArchiveRepository):
        self.repository = repository

    async def execute(self, collection_id: int, skip: int = 0, limit: int = 100) -> List[Box]:
        return await self.repository.list_boxes(collection_id, skip, limit)
