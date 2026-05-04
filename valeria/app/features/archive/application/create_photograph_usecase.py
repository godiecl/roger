from datetime import date
from typing import Optional
from app.features.archive.domain.archive import Photograph
from app.features.archive.domain.archive_port import IArchiveRepository
from app.shared.domain.exceptions import EntityNotFoundError


class CreatePhotographUseCase:
    def __init__(self, repository: IArchiveRepository):
        self.repository = repository

    async def execute(
        self,
        roll_id: int,
        frame_number: Optional[int] = None,
        identifier: Optional[str] = None,
        physical_location_ref: Optional[str] = None,
        digitalization_date: Optional[date] = None,
        width_px: Optional[int] = None,
        height_px: Optional[int] = None,
        color_depth: Optional[int] = None,
        resolution_dpi: Optional[float] = None,
        internal_cronology: Optional[str] = None,
        license: Optional[str] = None,
        copyright_notes: Optional[str] = None,
        is_public: bool = True,
        digitalized_by: Optional[int] = None,
        responsible_by: Optional[int] = None,
    ) -> Photograph:
        roll = await self.repository.get_roll(roll_id)
        if not roll:
            raise EntityNotFoundError(f"Rollo con id={roll_id} no encontrado")
        photograph = Photograph(
            roll_id=roll_id,
            frame_number=frame_number,
            identifier=identifier,
            physical_location_ref=physical_location_ref,
            digitalization_date=digitalization_date,
            width_px=width_px,
            height_px=height_px,
            color_depth=color_depth,
            resolution_dpi=resolution_dpi,
            internal_cronology=internal_cronology,
            license=license,
            copyright_notes=copyright_notes,
            is_public=is_public,
            digitalized_by=digitalized_by,
            responsible_by=responsible_by,
        )
        return await self.repository.create_photograph(photograph)
