from app.features.archive.domain.archive import Roll
from app.features.archive.domain.archive_port import IArchiveRepository
from app.shared.domain.exceptions import EntityNotFoundError


class GetRollUseCase:
    def __init__(self, repository: IArchiveRepository):
        self.repository = repository

    async def execute(self, roll_id: int) -> Roll:
        roll = await self.repository.get_roll(roll_id)
        if not roll:
            raise EntityNotFoundError(f"Rollo con id={roll_id} no encontrado")
        return roll
