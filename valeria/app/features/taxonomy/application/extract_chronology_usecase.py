"""
Use case: extract Attribute 02 (Chronological Dating) from a photograph file.

Flow:
  1. Verify the photograph exists and has at least one registered file.
  2. Create an AnalysisJob (status=RUNNING) for traceability.
  3. Call the configured chronology analyzer (stub or CLIP temporal).
  4. Supersede any existing ACTIVE record for this photograph.
  5. Write a new ACTIVE ChronologyDating record.
  6. Update the AnalysisJob to COMPLETED or FAILED.
  7. Return the new record.
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
    ChronologyDating,
)
from app.features.taxonomy.domain.taxonomy_port import ITaxonomyRepository
from app.infrastructure.analysis.analyzer_factory import create_chronology_analyzer
from app.shared.domain.exceptions import EntityNotFoundError


class ExtractChronologyUseCase:

    def __init__(self, repository: ITaxonomyRepository, session: AsyncSession):
        self.repository = repository
        self.session = session

    async def execute(self, photograph_id: int, triggered_by: int) -> ChronologyDating:
        # 1. Verify photograph exists
        photo_result = await self.session.execute(
            select(PhotographModel).where(PhotographModel.id == photograph_id)
        )
        if not photo_result.scalar_one_or_none():
            raise EntityNotFoundError(
                f"Fotografía con id={photograph_id} no encontrada"
            )

        # 2. Find best file (prefer JPG/TIFF for image-based models)
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

        # 3. Instantiate analyzer from factory (reads settings.attr02_analyzer)
        analyzer = create_chronology_analyzer()

        # 4. Create AnalysisJob
        job = AnalysisJobModel(
            photograph_id=photograph_id,
            attribute_type=AnalysisAttributeType.CHRONOLOGY,
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
                f"Error al analizar cronología para fotografía {photograph_id}: "
                f"{analysis['error']}"
            )

        # 6. Supersede existing ACTIVE records
        await self.repository.supersede_active_chronology(photograph_id)

        # 7. Save new record
        record = ChronologyDating(
            photograph_id=photograph_id,
            status=AttributeStatus.ACTIVE,
            source_type=SourceType.AI,
            date_type=analysis.get("date_type"),
            date_from=analysis.get("date_from"),
            date_to=analysis.get("date_to"),
            date_hypothesis=analysis.get("date_hypothesis"),
            methodology=analysis.get("methodology"),
            visual_evidence_notes=analysis.get("visual_evidence_notes"),
            analysis_provider=analysis.get("provider"),
            provider_version=analysis.get("provider_version"),
            confidence_level=analysis.get("confidence"),
            raw_output=analysis.get("raw_output"),
        )
        saved = await self.repository.save_chronology(record)

        # 8. Close job
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.now(timezone.utc)
        await self.session.flush()

        return saved
