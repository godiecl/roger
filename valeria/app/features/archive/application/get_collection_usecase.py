from app.features.archive.domain.archive import Collection
from app.features.archive.domain.archive_port import IArchiveRepository
from app.shared.domain.exceptions import EntityNotFoundError


class GetCollectionUseCase:

    def __init__(self, repository: IArchiveRepository):
        self.repository = repository

    async def execute(self, collection_id: int) -> Collection:
        collection = await self.repository.get_collection(collection_id)
        if not collection:
            raise EntityNotFoundError(f"Colección con id={collection_id} no encontrada.")
        return collection
