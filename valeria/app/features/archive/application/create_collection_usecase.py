from typing import Optional
from app.features.archive.domain.archive import Collection
from app.features.archive.domain.archive_port import IArchiveRepository
from app.shared.domain.exceptions import ValidationError, BusinessRuleViolationError


class CreateCollectionUseCase:

    def __init__(self, repository: IArchiveRepository):
        self.repository = repository

    async def execute(
        self,
        name: str,
        created_by: int,
        slug: Optional[str] = None,
        description: Optional[str] = None,
        photographer_name: Optional[str] = None,
        origin_country: Optional[str] = None,
        date_range_from: Optional[int] = None,
        date_range_to: Optional[int] = None,
        is_public: bool = True,
        cover_image_path: Optional[str] = None,
        license: Optional[str] = None,
        copyright_notes: Optional[str] = None,
    ) -> Collection:
        try:
            collection = Collection(
                name=name,
                slug=slug,
                description=description,
                photographer_name=photographer_name,
                origin_country=origin_country,
                date_range_from=date_range_from,
                date_range_to=date_range_to,
                is_public=is_public,
                cover_image_path=cover_image_path,
                license=license,
                copyright_notes=copyright_notes,
                created_by=created_by,
            )
        except ValueError as e:
            raise ValidationError(str(e))

        existing = await self.repository.get_collection_by_slug(collection.slug)
        if existing:
            raise BusinessRuleViolationError(
                f"Ya existe una colección con el slug '{collection.slug}'."
            )

        return await self.repository.create_collection(collection)
