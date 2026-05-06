"""
Use case: extract Attribute 04 (Environmental & Spatial Context) from a photograph file.

Flow mirrors ExtractChronologyUseCase with the environmental analyzer factory.
"""

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.features.archive.infrastructure.persistence.archive_model import (
    PhotographModel,
    PhotographFileModel,
    FileType,
)
from app.features.analysis.infrastructure.persistence.analysis_model import (
    AnalysisJobModel,
    JobStatus,
    AnalysisAttributeType,
)
from app.features.taxonomy.domain.taxonomy import (
    AttributeStatus,
    SourceType,
    EnvironmentalSpatial,
)
from app.features.taxonomy.domain.taxonomy_port import ITaxonomyRepository
from app.infrastructure.analysis.analyzer_factory import create_environmental_analyzer
from app.shared.domain.exceptions import EntityNotFoundError


class ExtractEnvironmentalUseCase:

    def __init__(self, repository: ITaxonomyRepository, session: AsyncSession):
        self.repository = repository
        self.session = session

    async def execute(self, photograph_id: int, triggered_by: int) -> EnvironmentalSpatial:
        # 1. Verify photograph
        result = await self.session.execute(
            select(PhotographModel).where(PhotographModel.id == photograph_id)
        )
        if not result.scalar_one_or_none():
            raise EntityNotFoundError(
                f"Fotografía con id={photograph_id} no encontrada"
            )

        # 2. Find best file
        files_result = await self.session.execute(
            select(PhotographFileModel)
            .where(PhotographFileModel.photograph_id == photograph_id)
            .order_by(PhotographFileModel.is_master.desc(), PhotographFileModel.id)
        )
        files = files_result.scalars().all()
        if not files:
            raise EntityNotFoundError(
                f"La fotografía {photograph_id} no tiene archivos registrados."
            )
        target = next(
            (f for f in files if f.file_type in (FileType.JPG, FileType.TIFF)),
            files[0],
        )

        # 3. Instantiate analyzer
        analyzer = create_environmental_analyzer()

        # 4. Create AnalysisJob
        job = AnalysisJobModel(
            photograph_id=photograph_id,
            attribute_type=AnalysisAttributeType.ENVIRONMENTAL,
            tool_name=analyzer.provider_name,
            tool_version=analyzer.provider_version,
            status=JobStatus.RUNNING,
            triggered_by=triggered_by,
            started_at=datetime.now(timezone.utc),
        )
        self.session.add(job)
        await self.session.flush()

        # 5. Run analysis
        analysis = analyzer.analyze(target.file_path)

        if analysis.get("error"):
            job.status = JobStatus.FAILED
            job.error_message = analysis["error"]
            job.completed_at = datetime.now(timezone.utc)
            await self.session.flush()
            raise RuntimeError(
                f"Error al analizar contexto ambiental para fotografía {photograph_id}: "
                f"{analysis['error']}"
            )

        # 6. Supersede existing ACTIVE records
        await self.repository.supersede_active_environmental(photograph_id)

        # 7. Save new record
        record = EnvironmentalSpatial(
            photograph_id=photograph_id,
            status=AttributeStatus.ACTIVE,
            source_type=SourceType.AI,
            setting_type=analysis.get("setting_type"),
            specific_typology=analysis.get("specific_typology"),
            conservation_state=analysis.get("conservation_state"),
            human_env_relationship=analysis.get("human_env_relationship"),
            analysis_provider=analysis.get("provider"),
            provider_version=analysis.get("provider_version"),
            confidence_level=analysis.get("confidence"),
            raw_output=analysis.get("raw_output"),
        )
        saved = await self.repository.save_environmental(record)

        # 8. Close job
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.now(timezone.utc)
        await self.session.flush()

        return saved
