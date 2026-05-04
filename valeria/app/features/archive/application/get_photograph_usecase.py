from app.features.archive.domain.archive import Photograph
from app.features.archive.domain.archive_port import IArchiveRepository
from app.shared.domain.exceptions import EntityNotFoundError


class GetPhotographUseCase:
    def __init__(self, repository: IArchiveRepository):
        self.repository = repository

    async def execute(self, photograph_id: int) -> Photograph:
        photo = await self.repository.get_photograph(photograph_id)
        if not photo:
            raise EntityNotFoundError(f"Fotografía con id={photograph_id} no encontrada")
        return photo
