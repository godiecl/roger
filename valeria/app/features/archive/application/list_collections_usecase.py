from typing import List
from app.features.archive.domain.archive import Collection
from app.features.archive.domain.archive_port import IArchiveRepository


class ListCollectionsUseCase:

    def __init__(self, repository: IArchiveRepository):
        self.repository = repository

    async def execute(self, skip: int = 0, limit: int = 100, public_only: bool = False) -> List[Collection]:
        return await self.repository.list_collections(skip=skip, limit=limit, public_only=public_only)
