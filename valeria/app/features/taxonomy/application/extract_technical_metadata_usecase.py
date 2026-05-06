"""
Use case: extract Attribute 01 (Technical Metadata) from a photograph file.

Flow:
  1. Verify the photograph exists and has at least one registered file.
  2. Create an AnalysisJob (status=RUNNING) for traceability.
  3. Call the Pillow analyzer on the best available file (master first, else first file).
  4. Supersede any existing ACTIVE record for this photograph.
  5. Write a new ACTIVE TechnicalMetadata record.
  6. Update the AnalysisJob to COMPLETED or FAILED.
  7. Return the new record.
"""

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.features.archive.infrastructure.persistence.archive_model import (
    PhotographModel, PhotographFileModel, FileType,
)
from app.features.analysis.infrastructure.persistence.analysis_model import (
    AnalysisJobModel, JobStatus, AnalysisAttributeType,
)
from app.features.taxonomy.domain.taxonomy import AttributeStatus, TechnicalMetadata
from app.features.taxonomy.domain.taxonomy_port import ITaxonomyRepository
from app.infrastructure.analysis import pillow_analyzer
from app.shared.domain.exceptions import EntityNotFoundError


class ExtractTechnicalMetadataUseCase:

    def __init__(self, repository: ITaxonomyRepository, session: AsyncSession):
        self.repository = repository
        self.session = session

    async def execute(self, photograph_id: int, triggered_by: int) -> TechnicalMetadata:
        # 1. Verify photograph exists
        photo_result = await self.session.execute(
            select(PhotographModel).where(PhotographModel.id == photograph_id)
        )
        photo = photo_result.scalar_one_or_none()
        if not photo:
            raise EntityNotFoundError(f"Fotografía con id={photograph_id} no encontrada")

        # 2. Find the best file to analyze (prefer master, then JPG/TIFF over CR3)
        files_result = await self.session.execute(
            select(PhotographFileModel)
            .where(PhotographFileModel.photograph_id == photograph_id)
            .order_by(PhotographFileModel.is_master.desc(), PhotographFileModel.id)
        )
        files = files_result.scalars().all()

        # Prefer non-CR3 for Pillow (JPG/TIFF), fall back to CR3 (needs ExifTool)
        target_file = None
        for f in files:
            if f.file_type in (FileType.JPG, FileType.TIFF):
                target_file = f
                break
        if not target_file and files:
            target_file = files[0]

        if not target_file:
            raise EntityNotFoundError(
                f"La fotografía {photograph_id} no tiene archivos registrados. "
                "Registra al menos un archivo antes de analizar."
            )

        # 3. Create AnalysisJob (running)
        job = AnalysisJobModel(
            photograph_id=photograph_id,
            attribute_type=AnalysisAttributeType.TECHNICAL,
            tool_name=pillow_analyzer.PROVIDER_NAME,
            tool_version=pillow_analyzer.PROVIDER_VERSION,
            status=JobStatus.RUNNING,
            triggered_by=triggered_by,
            started_at=datetime.now(timezone.utc),
        )
        self.session.add(job)
        await self.session.flush()

        # 4. Run analyzer
        analysis = pillow_analyzer.analyze(target_file.file_path)

        if analysis.get("error"):
            job.status = JobStatus.FAILED
            job.error_message = analysis["error"]
            job.completed_at = datetime.now(timezone.utc)
            await self.session.flush()
            raise RuntimeError(
                f"Error al analizar fotografía {photograph_id}: {analysis['error']}"
            )

        # 5. Supersede existing ACTIVE records
        await self.repository.supersede_active_technical(photograph_id)

        # 6. Build and save new TechnicalMetadata record
        record = TechnicalMetadata(
            photograph_id=photograph_id,
            status=AttributeStatus.ACTIVE,
            film_format="35mm",
            manufacturer=analysis.get("manufacturer"),
            iso_sensitivity=analysis.get("iso_sensitivity"),
            exposure=analysis.get("exposure"),
            diaphragm_aperture=analysis.get("diaphragm_aperture"),
            lens_optical=analysis.get("lens_optical"),
            camera_settings=analysis.get("camera_model"),
            is_estimated=False,
            analysis_provider=analysis.get("provider"),
            provider_version=analysis.get("provider_version"),
            raw_output=analysis.get("raw_exif"),
        )
        saved = await self.repository.save_technical_metadata(record)

        # 7. Auto-update photograph dimensions if they were missing
        width = analysis.get("width_px")
        height = analysis.get("height_px")
        if (width or height) and (not photo.width_px or not photo.height_px):
            if width:
                photo.width_px = int(width)
            if height:
                photo.height_px = int(height)
            await self.session.flush()

        # 8. Close job as COMPLETED
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.now(timezone.utc)
        await self.session.flush()

        return saved
