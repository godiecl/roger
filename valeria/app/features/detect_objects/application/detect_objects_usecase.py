from typing import List, Optional

import structlog

from app.features.detect_objects.domain.detection import Detection
from app.features.detect_objects.domain.detection_port import IDetectionRepository, IVisionAnalyzer
from app.shared.domain.exceptions import EntityNotFoundError

logger = structlog.get_logger()


class DetectObjectsUseCase:

    def __init__(self, analyzer: IVisionAnalyzer, repository: IDetectionRepository):
        self.analyzer = analyzer
        self.repository = repository

    async def execute(
        self,
        photograph_id: int,
        image_path: Optional[str] = None,
        image_url: Optional[str] = None,
        force_reanalysis: bool = False,
    ) -> Detection:
        logger.info("Iniciando detección de objetos", photograph_id=photograph_id)

        if not force_reanalysis:
            existing = await self.repository.get_by_photograph(photograph_id)
            if existing:
                logger.info("Retornando detección en caché", detection_id=existing.id)
                return existing

        detection = await self.analyzer.analyze(
            photograph_id=photograph_id,
            image_path=image_path,
            image_url=image_url,
        )

        saved = await self.repository.create(detection)

        logger.info(
            "Detección completada",
            detection_id=saved.id,
            object_count=saved.object_count(),
            provider=saved.provider,
            status=saved.status.value,
        )

        return saved

    async def get(self, detection_id: int) -> Detection:
        detection = await self.repository.get_by_id(detection_id)
        if not detection:
            raise EntityNotFoundError(f"Detección {detection_id} no encontrada.")
        return detection

    async def get_for_photograph(self, photograph_id: int) -> Optional[Detection]:
        return await self.repository.get_by_photograph(photograph_id)

    async def list(self, skip: int, limit: int) -> List[Detection]:
        return await self.repository.list(skip, limit)
