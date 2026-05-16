"""
ApproveContributionUseCase — the most complex use case in the contributions feature.

On approval:
  1. Validate contribution exists and is PENDING.
  2. Load current ACTIVE attr_* record (if any) to carry forward unrelated fields.
  3. Parse proposed_value to the correct Python type for the target field.
  4. Supersede the old ACTIVE record.
  5. Insert a new ACTIVE record with the contributed field merged in.
  6. Mark the contribution as APPROVED.

TAG contributions create/update a PhotographTag instead of an attr_* record.
"""

from datetime import datetime, date
from typing import Optional

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.features.contributions.domain.contribution import (
    Contribution, ContributionAttributeType, ContributionStatus,
)
from app.features.contributions.domain.contribution_port import IContributionRepository
from app.features.taxonomy.infrastructure.persistence.taxonomy_model import (
    AttrChronologyDatingModel,
    AttrGeographicReferenceModel,
    AttrEnvironmentalSpatialModel,
    AttributeStatus,
    SourceType,
    DateType,
    LocationType,
    SettingType,
    ConservationState,
)
from app.features.tagging.infrastructure.persistence.tag_model import (
    TagModel, PhotographTagModel, TagSource, TagStatus,
)
from app.shared.domain.exceptions import EntityNotFoundError, BusinessRuleViolationError, ValidationError


def _parse_value(field_name: str, raw: str):
    """Parse a proposed_value string to the right Python type for the given field."""
    float_fields = {"latitude", "longitude", "location_radius_km"}
    date_fields = {"precise_date", "date_from", "date_to"}
    enum_fields = {
        "date_type": DateType,
        "location_type": LocationType,
        "setting_type": SettingType,
        "conservation_state": ConservationState,
    }
    if field_name in float_fields:
        try:
            return float(raw)
        except ValueError:
            raise ValidationError(f"'{raw}' no es un número válido para el campo {field_name}.")
    if field_name in date_fields:
        try:
            return date.fromisoformat(raw)
        except ValueError:
            raise ValidationError(f"'{raw}' no es una fecha válida (esperado YYYY-MM-DD) para {field_name}.")
    if field_name in enum_fields:
        enum_cls = enum_fields[field_name]
        try:
            return enum_cls(raw)
        except ValueError:
            valid = [e.value for e in enum_cls]
            raise ValidationError(f"'{raw}' no es válido para {field_name}. Opciones: {valid}")
    return raw  # string fields


class ApproveContributionUseCase:

    def __init__(self, repository: IContributionRepository, session: AsyncSession):
        self.repository = repository
        self.session = session

    async def execute(self, contribution_id: int, reviewer_id: int) -> Contribution:
        # 1. Load contribution
        contribution = await self.repository.get_by_id(contribution_id)
        if not contribution:
            raise EntityNotFoundError(f"Contribución {contribution_id} no encontrada.")
        if not contribution.is_pending():
            raise BusinessRuleViolationError(
                f"Solo se pueden aprobar contribuciones PENDING. Estado actual: {contribution.status}"
            )

        parsed_value = _parse_value(contribution.field_name, contribution.proposed_value)

        attr_type = contribution.attribute_type

        if attr_type == ContributionAttributeType.GEOGRAPHIC:
            await self._apply_geographic(contribution, parsed_value)
        elif attr_type == ContributionAttributeType.ENVIRONMENTAL:
            await self._apply_environmental(contribution, parsed_value)
        elif attr_type == ContributionAttributeType.CHRONOLOGY:
            await self._apply_chronology(contribution, parsed_value)
        elif attr_type == ContributionAttributeType.TAG:
            await self._apply_tag(contribution, parsed_value, reviewer_id)

        # 6. Mark contribution approved
        return await self.repository.update_status(
            contribution_id=contribution_id,
            status=ContributionStatus.APPROVED,
            reviewed_by=reviewer_id,
        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    async def _apply_geographic(self, contribution: Contribution, value) -> None:
        current = await self._get_active(AttrGeographicReferenceModel, contribution.photograph_id)
        base = self._model_to_dict(current, [
            "location_type", "geographic_location", "latitude", "longitude",
            "location_radius_km", "signage_found", "architectural_landmarks", "landscape_features",
        ]) if current else {}
        base[contribution.field_name] = value

        if current:
            await self._supersede(AttrGeographicReferenceModel, contribution.photograph_id)

        self.session.add(AttrGeographicReferenceModel(
            photograph_id=contribution.photograph_id,
            status=AttributeStatus.ACTIVE,
            source_type=SourceType.USER_APPROVED,
            **base,
        ))
        await self.session.flush()

    async def _apply_environmental(self, contribution: Contribution, value) -> None:
        current = await self._get_active(AttrEnvironmentalSpatialModel, contribution.photograph_id)
        base = self._model_to_dict(current, [
            "setting_type", "specific_typology", "conservation_state", "human_env_relationship",
        ]) if current else {}
        base[contribution.field_name] = value

        if current:
            await self._supersede(AttrEnvironmentalSpatialModel, contribution.photograph_id)

        self.session.add(AttrEnvironmentalSpatialModel(
            photograph_id=contribution.photograph_id,
            status=AttributeStatus.ACTIVE,
            source_type=SourceType.USER_APPROVED,
            **base,
        ))
        await self.session.flush()

    async def _apply_chronology(self, contribution: Contribution, value) -> None:
        current = await self._get_active(AttrChronologyDatingModel, contribution.photograph_id)
        base = self._model_to_dict(current, [
            "date_type", "precise_date", "date_from", "date_to",
            "date_hypothesis", "verification_source", "methodology", "visual_evidence_notes",
        ]) if current else {}
        base[contribution.field_name] = value

        if current:
            await self._supersede(AttrChronologyDatingModel, contribution.photograph_id)

        self.session.add(AttrChronologyDatingModel(
            photograph_id=contribution.photograph_id,
            status=AttributeStatus.ACTIVE,
            source_type=SourceType.USER_APPROVED,
            **base,
        ))
        await self.session.flush()

    async def _apply_tag(self, contribution: Contribution, value, reviewer_id: int) -> None:
        """
        TAG contributions: field_name='tag_name' creates/reuses a Tag and links it
        to the photograph with source=USER_CONTRIBUTED, status=APPROVED.
        The curator who approved the contribution is recorded as approved_by.
        """
        if contribution.field_name != "tag_name":
            return  # tag_category handled as part of tag_name flow; skip standalone

        # Find or create the tag
        result = await self.session.execute(
            select(TagModel).where(TagModel.name == value)
        )
        tag = result.scalar_one_or_none()
        if not tag:
            tag = TagModel(name=value, category="iconographic")
            self.session.add(tag)
            await self.session.flush()
            await self.session.refresh(tag)

        # Check not already linked
        existing = await self.session.execute(
            select(PhotographTagModel).where(
                PhotographTagModel.photograph_id == contribution.photograph_id,
                PhotographTagModel.tag_id == tag.id,
            )
        )
        if not existing.scalar_one_or_none():
            self.session.add(PhotographTagModel(
                photograph_id=contribution.photograph_id,
                tag_id=tag.id,
                source=TagSource.USER_CONTRIBUTED,
                status=TagStatus.APPROVED,
                approved_by=reviewer_id,
                approved_at=datetime.utcnow(),
            ))
            await self.session.flush()

    async def _get_active(self, model_cls, photograph_id: int):
        result = await self.session.execute(
            select(model_cls)
            .where(
                model_cls.photograph_id == photograph_id,
                model_cls.status == AttributeStatus.ACTIVE,
            )
            .order_by(model_cls.id.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def _supersede(self, model_cls, photograph_id: int) -> None:
        await self.session.execute(
            update(model_cls)
            .where(
                model_cls.photograph_id == photograph_id,
                model_cls.status == AttributeStatus.ACTIVE,
            )
            .values(status=AttributeStatus.SUPERSEDED)
        )

    @staticmethod
    def _model_to_dict(model, fields: list) -> dict:
        return {f: getattr(model, f, None) for f in fields}
