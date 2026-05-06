from typing import Optional
from app.features.archive.domain.archive import Collection
from app.features.archive.domain.archive_port import IArchiveRepository
from app.shared.domain.exceptions import EntityNotFoundError, ValidationError


class UpdateCollectionUseCase:

    def __init__(self, repository: IArchiveRepository):
        self.repository = repository

    async def execute(
        self,
        collection_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        photographer_name: Optional[str] = None,
        origin_country: Optional[str] = None,
        date_range_from: Optional[int] = None,
        date_range_to: Optional[int] = None,
        is_public: Optional[bool] = None,
        cover_image_path: Optional[str] = None,
        license: Optional[str] = None,
        copyright_notes: Optional[str] = None,
    ) -> Collection:
        collection = await self.repository.get_collection(collection_id)
        if not collection:
            raise EntityNotFoundError(f"Colección con id={collection_id} no encontrada.")

        if name is not None:
            if not name.strip():
                raise ValidationError("El nombre no puede estar vacío.")
            collection.name = name.strip()
        if description is not None:
            collection.description = description
        if photographer_name is not None:
            collection.photographer_name = photographer_name
        if origin_country is not None:
            collection.origin_country = origin_country
        if date_range_from is not None:
            collection.date_range_from = date_range_from
        if date_range_to is not None:
            collection.date_range_to = date_range_to
        if is_public is not None:
            collection.is_public = is_public
        if cover_image_path is not None:
            collection.cover_image_path = cover_image_path
        if license is not None:
            collection.license = license
        if copyright_notes is not None:
            collection.copyright_notes = copyright_notes

        return await self.repository.update_collection(collection)
