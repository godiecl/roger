from typing import Optional
from app.features.archive.domain.archive import Box
from app.features.archive.domain.archive_port import IArchiveRepository
from app.shared.domain.exceptions import EntityNotFoundError


class GetBoxUseCase:
    def __init__(self, repository: IArchiveRepository):
        self.repository = repository

    async def execute(self, box_id: int) -> Box:
        box = await self.repository.get_box(box_id)
        if not box:
            raise EntityNotFoundError(f"Caja con id={box_id} no encontrada")
        return box
