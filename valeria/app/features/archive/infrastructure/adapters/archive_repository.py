"""
Archive repository implementation for ROGER - Valeria API.
"""

from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.features.archive.domain.archive import Collection, Box, Roll, Photograph, PhotographFile
from app.features.archive.domain.archive_port import IArchiveRepository
from app.features.archive.infrastructure.persistence.archive_model import (
    BoxModel, RollModel, PhotographModel, PhotographFileModel,
)
from app.features.view_images.infrastructure.persistence.image_model import CollectionModel


class ArchiveRepository(IArchiveRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    # ── Collections ───────────────────────────────────────────────────────────

    async def create_collection(self, collection: Collection) -> Collection:
        model = CollectionModel(
            name=collection.name,
            slug=collection.slug,
            description=collection.description,
            photographer_name=collection.photographer_name,
            origin_country=collection.origin_country,
            date_range_from=collection.date_range_from,
            date_range_to=collection.date_range_to,
            is_public=collection.is_public,
            cover_image_path=collection.cover_image_path,
            license=collection.license,
            copyright_notes=collection.copyright_notes,
            created_by=collection.created_by,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._collection_to_entity(model)

    async def get_collection(self, collection_id: int) -> Optional[Collection]:
        result = await self.session.execute(
            select(CollectionModel).where(CollectionModel.id == collection_id)
        )
        model = result.scalar_one_or_none()
        return self._collection_to_entity(model) if model else None

    async def get_collection_by_slug(self, slug: str) -> Optional[Collection]:
        result = await self.session.execute(
            select(CollectionModel).where(CollectionModel.slug == slug)
        )
        model = result.scalar_one_or_none()
        return self._collection_to_entity(model) if model else None

    async def list_collections(self, skip: int = 0, limit: int = 100, public_only: bool = False) -> List[Collection]:
        q = select(CollectionModel)
        if public_only:
            q = q.where(CollectionModel.is_public == True)
        q = q.order_by(CollectionModel.name).offset(skip).limit(limit)
        result = await self.session.execute(q)
        return [self._collection_to_entity(m) for m in result.scalars().all()]

    async def update_collection(self, collection: Collection) -> Collection:
        result = await self.session.execute(
            select(CollectionModel).where(CollectionModel.id == collection.id)
        )
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"Collection id={collection.id} not found")
        model.name = collection.name
        model.description = collection.description
        model.photographer_name = collection.photographer_name
        model.origin_country = collection.origin_country
        model.date_range_from = collection.date_range_from
        model.date_range_to = collection.date_range_to
        model.is_public = collection.is_public
        model.cover_image_path = collection.cover_image_path
        model.license = collection.license
        model.copyright_notes = collection.copyright_notes
        await self.session.flush()
        await self.session.refresh(model)
        return self._collection_to_entity(model)

    async def delete_collection(self, collection_id: int) -> bool:
        result = await self.session.execute(
            select(CollectionModel).where(CollectionModel.id == collection_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)
            return True
        return False

    def _collection_to_entity(self, m: CollectionModel) -> Collection:
        return Collection(
            id=m.id,
            name=m.name,
            slug=m.slug,
            description=m.description,
            photographer_name=m.photographer_name,
            origin_country=m.origin_country,
            date_range_from=m.date_range_from,
            date_range_to=m.date_range_to,
            is_public=m.is_public,
            cover_image_path=m.cover_image_path,
            license=m.license,
            copyright_notes=m.copyright_notes,
            created_by=m.created_by,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )

    # ── Boxes ─────────────────────────────────────────────────────────────────

    async def create_box(self, box: Box) -> Box:
        model = BoxModel(
            collection_id=box.collection_id,
            box_number=box.box_number,
            name=box.name,
            location_in_archive=box.location_in_archive,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._box_to_entity(model)

    async def get_box(self, box_id: int) -> Optional[Box]:
        result = await self.session.execute(select(BoxModel).where(BoxModel.id == box_id))
        model = result.scalar_one_or_none()
        return self._box_to_entity(model) if model else None

    async def list_boxes(self, collection_id: int, skip: int = 0, limit: int = 100) -> List[Box]:
        result = await self.session.execute(
            select(BoxModel)
            .where(BoxModel.collection_id == collection_id)
            .order_by(BoxModel.box_number)
            .offset(skip)
            .limit(limit)
        )
        return [self._box_to_entity(m) for m in result.scalars().all()]

    # ── Rolls ─────────────────────────────────────────────────────────────────

    async def create_roll(self, roll: Roll) -> Roll:
        model = RollModel(
            box_id=roll.box_id,
            general_number=roll.general_number,
            internal_number=roll.internal_number,
            og_number=roll.og_number,
            strip_letter=roll.strip_letter,
            name=roll.name,
            image_type=roll.image_type,
            support=roll.support,
            physical_status=roll.physical_status,
            color_mode=roll.color_mode,
            frame_count=roll.frame_count,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._roll_to_entity(model)

    async def get_roll(self, roll_id: int) -> Optional[Roll]:
        result = await self.session.execute(select(RollModel).where(RollModel.id == roll_id))
        model = result.scalar_one_or_none()
        return self._roll_to_entity(model) if model else None

    async def list_rolls(self, box_id: int, skip: int = 0, limit: int = 100) -> List[Roll]:
        result = await self.session.execute(
            select(RollModel)
            .where(RollModel.box_id == box_id)
            .order_by(RollModel.general_number)
            .offset(skip)
            .limit(limit)
        )
        return [self._roll_to_entity(m) for m in result.scalars().all()]

    # ── Photographs ───────────────────────────────────────────────────────────

    async def create_photograph(self, photograph: Photograph) -> Photograph:
        model = PhotographModel(
            roll_id=photograph.roll_id,
            frame_number=photograph.frame_number,
            identifier=photograph.identifier,
            physical_location_ref=photograph.physical_location_ref,
            digitalization_date=photograph.digitalization_date,
            width_px=photograph.width_px,
            height_px=photograph.height_px,
            color_depth=photograph.color_depth,
            resolution_dpi=photograph.resolution_dpi,
            internal_cronology=photograph.internal_cronology,
            license=photograph.license,
            copyright_notes=photograph.copyright_notes,
            is_public=photograph.is_public,
            digitalized_by=photograph.digitalized_by,
            responsible_by=photograph.responsible_by,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._photo_to_entity(model)

    async def get_photograph(self, photograph_id: int) -> Optional[Photograph]:
        result = await self.session.execute(
            select(PhotographModel).where(PhotographModel.id == photograph_id)
        )
        model = result.scalar_one_or_none()
        return self._photo_to_entity(model) if model else None

    async def list_photographs(self, roll_id: int, skip: int = 0, limit: int = 100) -> List[Photograph]:
        result = await self.session.execute(
            select(PhotographModel)
            .where(PhotographModel.roll_id == roll_id)
            .order_by(PhotographModel.frame_number)
            .offset(skip)
            .limit(limit)
        )
        return [self._photo_to_entity(m) for m in result.scalars().all()]

    # ── PhotographFiles ───────────────────────────────────────────────────────

    async def register_file(self, file: PhotographFile) -> PhotographFile:
        model = PhotographFileModel(
            photograph_id=file.photograph_id,
            file_type=file.file_type,
            file_path=file.file_path,
            is_master=file.is_master,
            file_size_bytes=file.file_size_bytes,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._file_to_entity(model)

    async def list_files(self, photograph_id: int) -> List[PhotographFile]:
        result = await self.session.execute(
            select(PhotographFileModel)
            .where(PhotographFileModel.photograph_id == photograph_id)
            .order_by(PhotographFileModel.is_master.desc(), PhotographFileModel.id)
        )
        return [self._file_to_entity(m) for m in result.scalars().all()]

    # ── Converters ────────────────────────────────────────────────────────────

    def _box_to_entity(self, m: BoxModel) -> Box:
        return Box(
            id=m.id, collection_id=m.collection_id, box_number=m.box_number,
            name=m.name, location_in_archive=m.location_in_archive,
            created_at=m.created_at, updated_at=m.updated_at,
        )

    def _roll_to_entity(self, m: RollModel) -> Roll:
        return Roll(
            id=m.id, box_id=m.box_id, general_number=m.general_number,
            internal_number=m.internal_number, og_number=m.og_number,
            strip_letter=m.strip_letter, name=m.name,
            image_type=m.image_type, support=m.support,
            physical_status=m.physical_status, color_mode=m.color_mode,
            frame_count=m.frame_count,
            created_at=m.created_at, updated_at=m.updated_at,
        )

    def _photo_to_entity(self, m: PhotographModel) -> Photograph:
        return Photograph(
            id=m.id, roll_id=m.roll_id, frame_number=m.frame_number,
            identifier=m.identifier, physical_location_ref=m.physical_location_ref,
            digitalization_date=m.digitalization_date,
            width_px=m.width_px, height_px=m.height_px,
            color_depth=m.color_depth, resolution_dpi=m.resolution_dpi,
            internal_cronology=m.internal_cronology,
            license=m.license, copyright_notes=m.copyright_notes,
            is_public=m.is_public, digitalized_by=m.digitalized_by,
            responsible_by=m.responsible_by,
            created_at=m.created_at, updated_at=m.updated_at,
        )

    def _file_to_entity(self, m: PhotographFileModel) -> PhotographFile:
        return PhotographFile(
            id=m.id, photograph_id=m.photograph_id,
            file_type=m.file_type, file_path=m.file_path,
            is_master=m.is_master, file_size_bytes=m.file_size_bytes,
            created_at=m.created_at, updated_at=m.updated_at,
        )
