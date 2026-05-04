from typing import Optional
from app.features.archive.domain.archive import Roll, ImageType, SupportType, PhysicalStatus, ColorMode
from app.features.archive.domain.archive_port import IArchiveRepository
from app.shared.domain.exceptions import EntityNotFoundError


class CreateRollUseCase:
    def __init__(self, repository: IArchiveRepository):
        self.repository = repository

    async def execute(
        self,
        box_id: int,
        general_number: Optional[int] = None,
        internal_number: Optional[int] = None,
        og_number: Optional[int] = None,
        strip_letter: Optional[str] = None,
        name: Optional[str] = None,
        image_type: Optional[ImageType] = None,
        support: Optional[SupportType] = None,
        physical_status: Optional[PhysicalStatus] = None,
        color_mode: Optional[ColorMode] = None,
        frame_count: Optional[int] = None,
    ) -> Roll:
        box = await self.repository.get_box(box_id)
        if not box:
            raise EntityNotFoundError(f"Caja con id={box_id} no encontrada")
        roll = Roll(
            box_id=box_id,
            general_number=general_number,
            internal_number=internal_number,
            og_number=og_number,
            strip_letter=strip_letter,
            name=name,
            image_type=image_type,
            support=support,
            physical_status=physical_status,
            color_mode=color_mode,
            frame_count=frame_count,
        )
        return await self.repository.create_roll(roll)
