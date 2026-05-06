"""
FastAPI routes for the archive feature.
Manages the physical hierarchy: Box → Roll → Photograph → PhotographFile.
Write operations require CURADOR or ADMINISTRADOR role.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.archive.application.create_collection_usecase import CreateCollectionUseCase
from app.features.archive.application.get_collection_usecase import GetCollectionUseCase
from app.features.archive.application.list_collections_usecase import ListCollectionsUseCase
from app.features.archive.application.update_collection_usecase import UpdateCollectionUseCase
from app.features.archive.application.create_box_usecase import CreateBoxUseCase
from app.features.archive.application.get_box_usecase import GetBoxUseCase
from app.features.archive.application.list_boxes_usecase import ListBoxesUseCase
from app.features.archive.application.create_roll_usecase import CreateRollUseCase
from app.features.archive.application.get_roll_usecase import GetRollUseCase
from app.features.archive.application.list_rolls_usecase import ListRollsUseCase
from app.features.archive.application.create_photograph_usecase import CreatePhotographUseCase
from app.features.archive.application.get_photograph_usecase import GetPhotographUseCase
from app.features.archive.application.list_photographs_usecase import ListPhotographsUseCase
from app.features.archive.application.register_file_usecase import RegisterPhotographFileUseCase
from app.features.archive.infrastructure.adapters.archive_repository import ArchiveRepository
from app.features.archive.interfaces.api.schemas import (
    CollectionCreateRequest, CollectionUpdateRequest, CollectionListResponse, CollectionResponse,
    BoxCreateRequest, BoxListResponse, BoxResponse,
    RollCreateRequest, RollListResponse, RollResponse,
    PhotographCreateRequest, PhotographListResponse, PhotographResponse,
    PhotographFileCreateRequest, PhotographFileListResponse, PhotographFileResponse,
)
from app.features.authenticate.domain.role import Role
from app.features.authenticate.infrastructure.adapters.user_repository import UserRepository
from app.features.authenticate.interfaces.api.dependencies import get_current_user_id
from app.infrastructure.database.session import get_db
from app.features.analysis.infrastructure.persistence.analysis_model import AnalysisJobModel
from app.features.taxonomy.application.extract_technical_metadata_usecase import ExtractTechnicalMetadataUseCase
from app.features.taxonomy.application.extract_chronology_usecase import ExtractChronologyUseCase
from app.features.taxonomy.application.extract_geographic_usecase import ExtractGeographicUseCase
from app.features.taxonomy.application.extract_environmental_usecase import ExtractEnvironmentalUseCase
from app.features.taxonomy.infrastructure.adapters.taxonomy_repository import TaxonomyRepository
from app.shared.domain.exceptions import EntityNotFoundError, ValidationError, BusinessRuleViolationError


router = APIRouter(prefix="/archive", tags=["Archive"])


async def _require_write_access(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> int:
    """Allow only CURADOR and ADMINISTRADOR to create/modify archive records."""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if not user or user.role not in (Role.CURADOR, Role.ADMINISTRADOR):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo curadores y administradores pueden modificar el archivo.",
        )
    return user_id


# ── Collections ───────────────────────────────────────────────────────────────

@router.post("/collections", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
async def create_collection(
    request: CollectionCreateRequest,
    user_id: int = Depends(_require_write_access),
    db: AsyncSession = Depends(get_db),
):
    try:
        repo = ArchiveRepository(db)
        usecase = CreateCollectionUseCase(repo)
        collection = await usecase.execute(
            name=request.name,
            created_by=user_id,
            slug=request.slug,
            description=request.description,
            photographer_name=request.photographer_name,
            origin_country=request.origin_country,
            date_range_from=request.date_range_from,
            date_range_to=request.date_range_to,
            is_public=request.is_public,
            cover_image_path=request.cover_image_path,
            license=request.license,
            copyright_notes=request.copyright_notes,
        )
        return CollectionResponse(**collection.__dict__)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except BusinessRuleViolationError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/collections", response_model=CollectionListResponse)
async def list_collections(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    public_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
):
    repo = ArchiveRepository(db)
    usecase = ListCollectionsUseCase(repo)
    collections = await usecase.execute(skip=skip, limit=limit, public_only=public_only)
    return CollectionListResponse(
        total=len(collections), skip=skip, limit=limit,
        collections=[CollectionResponse(**c.__dict__) for c in collections],
    )


@router.get("/collections/{collection_id}", response_model=CollectionResponse)
async def get_collection(
    collection_id: int,
    db: AsyncSession = Depends(get_db),
):
    try:
        repo = ArchiveRepository(db)
        usecase = GetCollectionUseCase(repo)
        collection = await usecase.execute(collection_id)
        return CollectionResponse(**collection.__dict__)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/collections/{collection_id}", response_model=CollectionResponse)
async def update_collection(
    collection_id: int,
    request: CollectionUpdateRequest,
    _: int = Depends(_require_write_access),
    db: AsyncSession = Depends(get_db),
):
    try:
        repo = ArchiveRepository(db)
        usecase = UpdateCollectionUseCase(repo)
        collection = await usecase.execute(
            collection_id=collection_id,
            name=request.name,
            description=request.description,
            photographer_name=request.photographer_name,
            origin_country=request.origin_country,
            date_range_from=request.date_range_from,
            date_range_to=request.date_range_to,
            is_public=request.is_public,
            cover_image_path=request.cover_image_path,
            license=request.license,
            copyright_notes=request.copyright_notes,
        )
        return CollectionResponse(**collection.__dict__)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/collections/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_collection(
    collection_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if not user or user.role != Role.ADMINISTRADOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo administradores pueden eliminar colecciones.")
    repo = ArchiveRepository(db)
    deleted = await repo.delete_collection(collection_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Colección no encontrada.")
    return None


# ── Boxes ─────────────────────────────────────────────────────────────────────

@router.post("/boxes", response_model=BoxResponse, status_code=status.HTTP_201_CREATED)
async def create_box(
    request: BoxCreateRequest,
    _: int = Depends(_require_write_access),
    db: AsyncSession = Depends(get_db),
):
    try:
        repo = ArchiveRepository(db)
        usecase = CreateBoxUseCase(repo)
        box = await usecase.execute(
            collection_id=request.collection_id,
            box_number=request.box_number,
            name=request.name,
            location_in_archive=request.location_in_archive,
        )
        return BoxResponse(**box.__dict__)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/boxes", response_model=BoxListResponse)
async def list_boxes(
    collection_id: int = Query(..., description="ID de la colección"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    _: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = ArchiveRepository(db)
    usecase = ListBoxesUseCase(repo)
    boxes = await usecase.execute(collection_id=collection_id, skip=skip, limit=limit)
    return BoxListResponse(total=len(boxes), skip=skip, limit=limit, boxes=[BoxResponse(**b.__dict__) for b in boxes])


@router.get("/boxes/{box_id}", response_model=BoxResponse)
async def get_box(
    box_id: int,
    _: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    try:
        repo = ArchiveRepository(db)
        usecase = GetBoxUseCase(repo)
        box = await usecase.execute(box_id)
        return BoxResponse(**box.__dict__)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ── Rolls ─────────────────────────────────────────────────────────────────────

@router.post("/rolls", response_model=RollResponse, status_code=status.HTTP_201_CREATED)
async def create_roll(
    request: RollCreateRequest,
    _: int = Depends(_require_write_access),
    db: AsyncSession = Depends(get_db),
):
    try:
        repo = ArchiveRepository(db)
        usecase = CreateRollUseCase(repo)
        roll = await usecase.execute(
            box_id=request.box_id,
            general_number=request.general_number,
            internal_number=request.internal_number,
            og_number=request.og_number,
            strip_letter=request.strip_letter,
            name=request.name,
            image_type=request.image_type,
            support=request.support,
            physical_status=request.physical_status,
            color_mode=request.color_mode,
            frame_count=request.frame_count,
        )
        return RollResponse(**roll.__dict__)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/boxes/{box_id}/rolls", response_model=RollListResponse)
async def list_rolls(
    box_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    _: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = ArchiveRepository(db)
    usecase = ListRollsUseCase(repo)
    rolls = await usecase.execute(box_id=box_id, skip=skip, limit=limit)
    return RollListResponse(total=len(rolls), skip=skip, limit=limit, rolls=[RollResponse(**r.__dict__) for r in rolls])


@router.get("/rolls/{roll_id}", response_model=RollResponse)
async def get_roll(
    roll_id: int,
    _: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    try:
        repo = ArchiveRepository(db)
        usecase = GetRollUseCase(repo)
        roll = await usecase.execute(roll_id)
        return RollResponse(**roll.__dict__)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ── Photographs ───────────────────────────────────────────────────────────────

@router.post("/photographs", response_model=PhotographResponse, status_code=status.HTTP_201_CREATED)
async def create_photograph(
    request: PhotographCreateRequest,
    _: int = Depends(_require_write_access),
    db: AsyncSession = Depends(get_db),
):
    try:
        repo = ArchiveRepository(db)
        usecase = CreatePhotographUseCase(repo)
        photo = await usecase.execute(
            roll_id=request.roll_id,
            frame_number=request.frame_number,
            identifier=request.identifier,
            physical_location_ref=request.physical_location_ref,
            digitalization_date=request.digitalization_date,
            width_px=request.width_px,
            height_px=request.height_px,
            color_depth=request.color_depth,
            resolution_dpi=request.resolution_dpi,
            internal_cronology=request.internal_cronology,
            license=request.license,
            copyright_notes=request.copyright_notes,
            is_public=request.is_public,
            digitalized_by=request.digitalized_by,
            responsible_by=request.responsible_by,
        )
        return PhotographResponse(**photo.__dict__)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/rolls/{roll_id}/photographs", response_model=PhotographListResponse)
async def list_photographs(
    roll_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    _: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = ArchiveRepository(db)
    usecase = ListPhotographsUseCase(repo)
    photos = await usecase.execute(roll_id=roll_id, skip=skip, limit=limit)
    return PhotographListResponse(
        total=len(photos), skip=skip, limit=limit,
        photographs=[PhotographResponse(**p.__dict__) for p in photos],
    )


@router.get("/photographs/{photograph_id}", response_model=PhotographResponse)
async def get_photograph(
    photograph_id: int,
    _: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    try:
        repo = ArchiveRepository(db)
        usecase = GetPhotographUseCase(repo)
        photo = await usecase.execute(photograph_id)
        return PhotographResponse(**photo.__dict__)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ── PhotographFiles ───────────────────────────────────────────────────────────

class PhotographFileWithAnalysisResponse(PhotographFileResponse):
    analysis_triggered: bool = False
    analysis_error: Optional[str] = None


@router.post(
    "/photographs/{photograph_id}/files",
    response_model=PhotographFileWithAnalysisResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_file(
    photograph_id: int,
    request: PhotographFileCreateRequest,
    user_id: int = Depends(_require_write_access),
    db: AsyncSession = Depends(get_db),
):
    try:
        repo = ArchiveRepository(db)
        usecase = RegisterPhotographFileUseCase(repo)
        pf = await usecase.execute(
            photograph_id=photograph_id,
            file_type=request.file_type,
            file_path=request.file_path,
            is_master=request.is_master,
            file_size_bytes=request.file_size_bytes,
        )
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    analysis_triggered = False
    analysis_errors: list[str] = []

    if request.is_master:
        analysis_triggered = True
        tax_repo = TaxonomyRepository(db)
        for UseCase in (
            ExtractTechnicalMetadataUseCase,
            ExtractChronologyUseCase,
            ExtractGeographicUseCase,
            ExtractEnvironmentalUseCase,
        ):
            try:
                await UseCase(tax_repo, db).execute(photograph_id, triggered_by=user_id)
            except Exception as exc:
                analysis_errors.append(str(exc))

    return PhotographFileWithAnalysisResponse(
        **pf.__dict__,
        analysis_triggered=analysis_triggered,
        analysis_error="; ".join(analysis_errors) if analysis_errors else None,
    )


@router.get("/photographs/{photograph_id}/files", response_model=PhotographFileListResponse)
async def list_files(
    photograph_id: int,
    _: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = ArchiveRepository(db)
    files = await repo.list_files(photograph_id)
    return PhotographFileListResponse(
        total=len(files),
        files=[PhotographFileResponse(**f.__dict__) for f in files],
    )


# ── Analysis Jobs ─────────────────────────────────────────────────────────────

from datetime import datetime
from pydantic import BaseModel as PydanticModel
from sqlalchemy.future import select as sa_select


class AnalysisJobResponse(PydanticModel):
    id: int
    photograph_id: int
    attribute_type: str
    tool_name: str
    tool_version: Optional[str]
    status: str
    triggered_by: Optional[int]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


@router.get("/photographs/{photograph_id}/jobs", response_model=List[AnalysisJobResponse])
async def list_analysis_jobs(
    photograph_id: int,
    _: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """List all analysis jobs for a photograph (full traceability)."""
    result = await db.execute(
        sa_select(AnalysisJobModel)
        .where(AnalysisJobModel.photograph_id == photograph_id)
        .order_by(AnalysisJobModel.created_at.desc())
    )
    jobs = result.scalars().all()
    return [AnalysisJobResponse(
        id=j.id, photograph_id=j.photograph_id,
        attribute_type=j.attribute_type.value if hasattr(j.attribute_type, 'value') else str(j.attribute_type),
        tool_name=j.tool_name, tool_version=j.tool_version,
        status=j.status.value if hasattr(j.status, 'value') else str(j.status),
        triggered_by=j.triggered_by,
        started_at=j.started_at, completed_at=j.completed_at,
        error_message=j.error_message, created_at=j.created_at,
    ) for j in jobs]
