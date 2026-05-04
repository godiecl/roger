"""
Taxonomy repository implementation for ROGER - Valeria API.
"""

from typing import List, Optional

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.features.taxonomy.domain.taxonomy import AttributeStatus, TechnicalMetadata
from app.features.taxonomy.domain.taxonomy_port import ITaxonomyRepository
from app.features.taxonomy.infrastructure.persistence.taxonomy_model import AttrTechnicalMetadataModel


class TaxonomyRepository(ITaxonomyRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_technical_metadata(self, record: TechnicalMetadata) -> TechnicalMetadata:
        model = AttrTechnicalMetadataModel(
            photograph_id=record.photograph_id,
            status=record.status,
            film_format=record.film_format,
            manufacturer=record.manufacturer,
            emulsion_type=record.emulsion_type,
            iso_sensitivity=record.iso_sensitivity,
            mounting_marks=record.mounting_marks,
            scanning_artifacts=record.scanning_artifacts,
            physical_status=record.physical_status,
            exposure=record.exposure,
            diaphragm_aperture=record.diaphragm_aperture,
            lens_optical=record.lens_optical,
            camera_settings=record.camera_settings,
            deterioration_notes=record.deterioration_notes,
            digitizer_person=record.digitizer_person,
            is_estimated=record.is_estimated,
            analysis_provider=record.analysis_provider,
            provider_version=record.provider_version,
            confidence_level=record.confidence_level,
            raw_output=record.raw_output,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def supersede_active_technical(self, photograph_id: int) -> None:
        await self.session.execute(
            update(AttrTechnicalMetadataModel)
            .where(
                AttrTechnicalMetadataModel.photograph_id == photograph_id,
                AttrTechnicalMetadataModel.status == AttributeStatus.ACTIVE,
            )
            .values(status=AttributeStatus.SUPERSEDED)
        )

    async def get_active_technical(self, photograph_id: int) -> Optional[TechnicalMetadata]:
        result = await self.session.execute(
            select(AttrTechnicalMetadataModel)
            .where(
                AttrTechnicalMetadataModel.photograph_id == photograph_id,
                AttrTechnicalMetadataModel.status == AttributeStatus.ACTIVE,
            )
            .order_by(AttrTechnicalMetadataModel.id.desc())
            .limit(1)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_technical_history(self, photograph_id: int) -> List[TechnicalMetadata]:
        result = await self.session.execute(
            select(AttrTechnicalMetadataModel)
            .where(AttrTechnicalMetadataModel.photograph_id == photograph_id)
            .order_by(AttrTechnicalMetadataModel.id.desc())
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    def _to_entity(self, m: AttrTechnicalMetadataModel) -> TechnicalMetadata:
        return TechnicalMetadata(
            id=m.id,
            photograph_id=m.photograph_id,
            status=m.status,
            film_format=m.film_format,
            manufacturer=m.manufacturer,
            emulsion_type=m.emulsion_type,
            iso_sensitivity=m.iso_sensitivity,
            mounting_marks=m.mounting_marks,
            scanning_artifacts=m.scanning_artifacts,
            physical_status=m.physical_status,
            exposure=m.exposure,
            diaphragm_aperture=m.diaphragm_aperture,
            lens_optical=m.lens_optical,
            camera_settings=m.camera_settings,
            deterioration_notes=m.deterioration_notes,
            digitizer_person=m.digitizer_person,
            is_estimated=m.is_estimated,
            analysis_provider=m.analysis_provider,
            provider_version=m.provider_version,
            confidence_level=m.confidence_level,
            raw_output=m.raw_output,
            analyzed_at=m.analyzed_at,
        )
