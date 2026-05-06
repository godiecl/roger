from app.features.contributions.domain.contribution import (
    ALLOWED_FIELDS, Contribution, ContributionAttributeType, ContributionStatus,
)
from app.features.contributions.domain.contribution_port import IContributionRepository
from app.shared.domain.exceptions import ValidationError


class SubmitContributionUseCase:

    def __init__(self, repository: IContributionRepository):
        self.repository = repository

    async def execute(
        self,
        photograph_id: int,
        contributor_id: int,
        attribute_type: ContributionAttributeType,
        field_name: str,
        proposed_value: str,
        evidence_notes: str = None,
    ) -> Contribution:
        allowed = ALLOWED_FIELDS.get(attribute_type, set())
        if field_name not in allowed:
            raise ValidationError(
                f"El campo '{field_name}' no es válido para el atributo '{attribute_type}'. "
                f"Campos permitidos: {sorted(allowed)}"
            )
        if not proposed_value or not proposed_value.strip():
            raise ValidationError("El valor propuesto no puede estar vacío.")

        contribution = Contribution(
            photograph_id=photograph_id,
            contributor_id=contributor_id,
            attribute_type=attribute_type,
            field_name=field_name,
            proposed_value=proposed_value.strip(),
            evidence_notes=evidence_notes,
            status=ContributionStatus.PENDING,
        )
        return await self.repository.create(contribution)
