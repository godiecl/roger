from typing import Optional
from app.features.archive.domain.archive import PhotographFile, FileType
from app.features.archive.domain.archive_port import IArchiveRepository
from app.shared.domain.exceptions import EntityNotFoundError, ValidationError


class RegisterPhotographFileUseCase:
    def __init__(self, repository: IArchiveRepository):
        self.repository = repository

    async def execute(
        self,
        photograph_id: int,
        file_type: FileType,
        file_path: str,
        is_master: bool = False,
        file_size_bytes: Optional[int] = None,
    ) -> PhotographFile:
        photo = await self.repository.get_photograph(photograph_id)
        if not photo:
            raise EntityNotFoundError(f"Fotografía con id={photograph_id} no encontrada")
        if not file_path or not file_path.strip():
            raise ValidationError("La ruta del archivo no puede estar vacía")
        pf = PhotographFile(
            photograph_id=photograph_id,
            file_type=file_type,
            file_path=file_path.strip(),
            is_master=is_master,
            file_size_bytes=file_size_bytes,
        )
        return await self.repository.register_file(pf)
