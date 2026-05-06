from typing import Optional
from app.features.archive.domain.archive import Box
from app.features.archive.domain.archive_port import IArchiveRepository
from app.shared.domain.exceptions import ValidationError


class CreateBoxUseCase:
    def __init__(self, repository: IArchiveRepository):
        self.repository = repository

    async def execute(
        self,
        collection_id: int,
        box_number: int,
        name: Optional[str] = None,
        location_in_archive: Optional[str] = None,
    ) -> Box:
        if box_number < 1:
            raise ValidationError("El número de caja debe ser mayor a 0")
        box = Box(
            collection_id=collection_id,
            box_number=box_number,
            name=name,
            location_in_archive=location_in_archive,
        )
        return await self.repository.create_box(box)
