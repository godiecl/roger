from typing import List, Optional

from app.features.taxonomy.domain.taxonomy import TechnicalMetadata
from app.features.taxonomy.domain.taxonomy_port import ITaxonomyRepository
from app.shared.domain.exceptions import EntityNotFoundError


class GetTechnicalMetadataUseCase:

    def __init__(self, repository: ITaxonomyRepository):
        self.repository = repository

    async def execute_active(self, photograph_id: int) -> TechnicalMetadata:
        record = await self.repository.get_active_technical(photograph_id)
        if not record:
            raise EntityNotFoundError(
                f"No hay metadatos técnicos activos para la fotografía {photograph_id}. "
                "Ejecuta el análisis primero."
            )
        return record

    async def execute_history(self, photograph_id: int) -> List[TechnicalMetadata]:
        return await self.repository.list_technical_history(photograph_id)
