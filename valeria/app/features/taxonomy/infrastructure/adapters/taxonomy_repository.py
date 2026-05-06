"""
Taxonomy repository implementation for ROGER - Valeria API.
Covers Attributes 01-04: Technical, Chronology, Geographic, Environmental.
"""

from typing import List, Optional

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.features.taxonomy.domain.taxonomy import (
    AttributeStatus,
    SourceType,
    TechnicalMetadata,
    ChronologyDating,
    GeographicReference,
    EnvironmentalSpatial,
)
from app.features.taxonomy.domain.taxonomy_port import ITaxonomyRepository
from app.features.taxonomy.infrastructure.persistence.taxonomy_model import (
    AttrTechnicalMetadataModel,
    AttrChronologyDatingModel,
    AttrGeographicReferenceModel,
    AttrEnvironmentalSpatialModel,
)


class TaxonomyRepository(ITaxonomyRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    # ── Attribute 01 — Technical Metadata ────────────────────────────────────

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
        return self._technical_to_entity(model)

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
        return self._technical_to_entity(model) if model else None

    async def list_technical_history(self, photograph_id: int) -> List[TechnicalMetadata]:
        result = await self.session.execute(
            select(AttrTechnicalMetadataModel)
            .where(AttrTechnicalMetadataModel.photograph_id == photograph_id)
            .order_by(AttrTechnicalMetadataModel.id.desc())
        )
        return [self._technical_to_entity(m) for m in result.scalars().all()]

    def _technical_to_entity(self, m: AttrTechnicalMetadataModel) -> TechnicalMetadata:
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

    # ── Attribute 02 — Chronological Dating ──────────────────────────────────

    async def save_chronology(self, record: ChronologyDating) -> ChronologyDating:
        model = AttrChronologyDatingModel(
            photograph_id=record.photograph_id,
            status=record.status,
            source_type=record.source_type,
            date_type=record.date_type,
            precise_date=record.precise_date,
            date_from=record.date_from,
            date_to=record.date_to,
            date_hypothesis=record.date_hypothesis,
            verification_source=record.verification_source,
            methodology=record.methodology,
            visual_evidence_notes=record.visual_evidence_notes,
            analysis_provider=record.analysis_provider,
            provider_version=record.provider_version,
            confidence_level=record.confidence_level,
            raw_output=record.raw_output,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._chronology_to_entity(model)

    async def supersede_active_chronology(self, photograph_id: int) -> None:
        await self.session.execute(
            update(AttrChronologyDatingModel)
            .where(
                AttrChronologyDatingModel.photograph_id == photograph_id,
                AttrChronologyDatingModel.status == AttributeStatus.ACTIVE,
            )
            .values(status=AttributeStatus.SUPERSEDED)
        )

    async def get_active_chronology(self, photograph_id: int) -> Optional[ChronologyDating]:
        result = await self.session.execute(
            select(AttrChronologyDatingModel)
            .where(
                AttrChronologyDatingModel.photograph_id == photograph_id,
                AttrChronologyDatingModel.status == AttributeStatus.ACTIVE,
            )
            .order_by(AttrChronologyDatingModel.id.desc())
            .limit(1)
        )
        model = result.scalar_one_or_none()
        return self._chronology_to_entity(model) if model else None

    async def list_chronology_history(self, photograph_id: int) -> List[ChronologyDating]:
        result = await self.session.execute(
            select(AttrChronologyDatingModel)
            .where(AttrChronologyDatingModel.photograph_id == photograph_id)
            .order_by(AttrChronologyDatingModel.id.desc())
        )
        return [self._chronology_to_entity(m) for m in result.scalars().all()]

    def _chronology_to_entity(self, m: AttrChronologyDatingModel) -> ChronologyDating:
        return ChronologyDating(
            id=m.id,
            photograph_id=m.photograph_id,
            status=m.status,
            source_type=m.source_type,
            date_type=m.date_type,
            precise_date=m.precise_date,
            date_from=m.date_from,
            date_to=m.date_to,
            date_hypothesis=m.date_hypothesis,
            verification_source=m.verification_source,
            methodology=m.methodology,
            visual_evidence_notes=m.visual_evidence_notes,
            analysis_provider=m.analysis_provider,
            provider_version=m.provider_version,
            confidence_level=m.confidence_level,
            raw_output=m.raw_output,
            analyzed_at=m.analyzed_at,
        )

    # ── Attribute 03 — Geographic Reference ──────────────────────────────────

    async def save_geographic(self, record: GeographicReference) -> GeographicReference:
        model = AttrGeographicReferenceModel(
            photograph_id=record.photograph_id,
            status=record.status,
            source_type=record.source_type,
            location_type=record.location_type,
            geographic_location=record.geographic_location,
            latitude=record.latitude,
            longitude=record.longitude,
            location_radius_km=record.location_radius_km,
            signage_found=record.signage_found,
            architectural_landmarks=record.architectural_landmarks,
            landscape_features=record.landscape_features,
            analysis_provider=record.analysis_provider,
            provider_version=record.provider_version,
            confidence_level=record.confidence_level,
            raw_output=record.raw_output,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._geographic_to_entity(model)

    async def supersede_active_geographic(self, photograph_id: int) -> None:
        await self.session.execute(
            update(AttrGeographicReferenceModel)
            .where(
                AttrGeographicReferenceModel.photograph_id == photograph_id,
                AttrGeographicReferenceModel.status == AttributeStatus.ACTIVE,
            )
            .values(status=AttributeStatus.SUPERSEDED)
        )

    async def get_active_geographic(
        self, photograph_id: int
    ) -> Optional[GeographicReference]:
        result = await self.session.execute(
            select(AttrGeographicReferenceModel)
            .where(
                AttrGeographicReferenceModel.photograph_id == photograph_id,
                AttrGeographicReferenceModel.status == AttributeStatus.ACTIVE,
            )
            .order_by(AttrGeographicReferenceModel.id.desc())
            .limit(1)
        )
        model = result.scalar_one_or_none()
        return self._geographic_to_entity(model) if model else None

    async def list_geographic_history(
        self, photograph_id: int
    ) -> List[GeographicReference]:
        result = await self.session.execute(
            select(AttrGeographicReferenceModel)
            .where(AttrGeographicReferenceModel.photograph_id == photograph_id)
            .order_by(AttrGeographicReferenceModel.id.desc())
        )
        return [self._geographic_to_entity(m) for m in result.scalars().all()]

    def _geographic_to_entity(self, m: AttrGeographicReferenceModel) -> GeographicReference:
        return GeographicReference(
            id=m.id,
            photograph_id=m.photograph_id,
            status=m.status,
            source_type=m.source_type,
            location_type=m.location_type,
            geographic_location=m.geographic_location,
            latitude=m.latitude,
            longitude=m.longitude,
            location_radius_km=m.location_radius_km,
            signage_found=m.signage_found,
            architectural_landmarks=m.architectural_landmarks,
            landscape_features=m.landscape_features,
            analysis_provider=m.analysis_provider,
            provider_version=m.provider_version,
            confidence_level=m.confidence_level,
            raw_output=m.raw_output,
            analyzed_at=m.analyzed_at,
        )

    # ── Attribute 04 — Environmental & Spatial Context ───────────────────────

    async def save_environmental(self, record: EnvironmentalSpatial) -> EnvironmentalSpatial:
        model = AttrEnvironmentalSpatialModel(
            photograph_id=record.photograph_id,
            status=record.status,
            source_type=record.source_type,
            setting_type=record.setting_type,
            specific_typology=record.specific_typology,
            conservation_state=record.conservation_state,
            human_env_relationship=record.human_env_relationship,
            analysis_provider=record.analysis_provider,
            provider_version=record.provider_version,
            confidence_level=record.confidence_level,
            raw_output=record.raw_output,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._environmental_to_entity(model)

    async def supersede_active_environmental(self, photograph_id: int) -> None:
        await self.session.execute(
            update(AttrEnvironmentalSpatialModel)
            .where(
                AttrEnvironmentalSpatialModel.photograph_id == photograph_id,
                AttrEnvironmentalSpatialModel.status == AttributeStatus.ACTIVE,
            )
            .values(status=AttributeStatus.SUPERSEDED)
        )

    async def get_active_environmental(
        self, photograph_id: int
    ) -> Optional[EnvironmentalSpatial]:
        result = await self.session.execute(
            select(AttrEnvironmentalSpatialModel)
            .where(
                AttrEnvironmentalSpatialModel.photograph_id == photograph_id,
                AttrEnvironmentalSpatialModel.status == AttributeStatus.ACTIVE,
            )
            .order_by(AttrEnvironmentalSpatialModel.id.desc())
            .limit(1)
        )
        model = result.scalar_one_or_none()
        return self._environmental_to_entity(model) if model else None

    async def list_environmental_history(
        self, photograph_id: int
    ) -> List[EnvironmentalSpatial]:
        result = await self.session.execute(
            select(AttrEnvironmentalSpatialModel)
            .where(AttrEnvironmentalSpatialModel.photograph_id == photograph_id)
            .order_by(AttrEnvironmentalSpatialModel.id.desc())
        )
        return [self._environmental_to_entity(m) for m in result.scalars().all()]

    def _environmental_to_entity(
        self, m: AttrEnvironmentalSpatialModel
    ) -> EnvironmentalSpatial:
        return EnvironmentalSpatial(
            id=m.id,
            photograph_id=m.photograph_id,
            status=m.status,
            source_type=m.source_type,
            setting_type=m.setting_type,
            specific_typology=m.specific_typology,
            conservation_state=m.conservation_state,
            human_env_relationship=m.human_env_relationship,
            analysis_provider=m.analysis_provider,
            provider_version=m.provider_version,
            confidence_level=m.confidence_level,
            raw_output=m.raw_output,
            analyzed_at=m.analyzed_at,
        )
