"""
FastAPI routes for the archive feature.
Manages the physical hierarchy: Box → Roll → Photograph → PhotographFile.
Write operations require CURADOR or ADMINISTRADOR role.
"""

import re
import uuid
from io import BytesIO
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
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
    db: AsyncSession = Depends(get_db),
):
    repo = ArchiveRepository(db)
    usecase = ListCollectionsUseCase(repo)
    collections = await usecase.execute(skip=skip, limit=limit, public_only=True)
    return CollectionListResponse(
        total=len(collections), skip=skip, limit=limit,
        collections=[CollectionResponse(**c.__dict__) for c in collections],
    )


@router.get("/collections/all", response_model=CollectionListResponse)
async def list_all_collections(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    _: int = Depends(_require_write_access),
    db: AsyncSession = Depends(get_db),
):
    """List all collections including private ones. Requires curator or admin role."""
    repo = ArchiveRepository(db)
    usecase = ListCollectionsUseCase(repo)
    collections = await usecase.execute(skip=skip, limit=limit, public_only=False)
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
        if not collection.is_public:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Colección no encontrada.",
            )
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

    # Cascade: remove all images in this collection before deleting the collection record
    from sqlalchemy import delete as sql_delete
    from app.features.view_images.infrastructure.persistence.image_model import ImageModel
    await db.execute(sql_delete(ImageModel).where(ImageModel.collection_id == collection_id))

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


# ── Upload helpers ────────────────────────────────────────────────────────────

_ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp", "image/tiff", "image/gif"}
_ALLOWED_EXT  = {".jpg", ".jpeg", ".png", ".webp", ".tiff", ".tif", ".gif"}
_MAX_BYTES = 50 * 1024 * 1024  # 50 MB


def _safe_filename(name: str) -> str:
    stem = Path(name).stem
    ext  = Path(name).suffix.lower()
    stem = re.sub(r"[^\w\-]", "_", stem)[:80]
    return f"{stem}{ext}"


def _slugify(text: str, max_len: int = 60) -> str:
    return re.sub(r"[^\w\-]", "_", text.strip())[:max_len]


async def _save_upload(
    file: UploadFile,
    collection_slug: str,
    box: str | None = None,
    subdivision: str | None = None,
) -> tuple[str, int]:
    """
    Write UploadFile to disk.
    Path: storage/images/{collection}/{box}/{subdivision}/{uuid}_{name}.jpg
    box and subdivision are optional; omitting them gives a flat collection folder.
    Returns (relative_path_for_url, size_bytes).
    """
    ext = Path(file.filename or "photo.jpg").suffix.lower()
    if ext not in _ALLOWED_EXT:
        raise HTTPException(status_code=400, detail=f"Tipo de archivo no permitido: {ext}")

    content = await file.read()
    size = len(content)
    if size == 0:
        raise HTTPException(status_code=400, detail="El archivo está vacío.")
    if size > _MAX_BYTES:
        raise HTTPException(status_code=413, detail=f"Archivo demasiado grande ({size // 1024 // 1024} MB). Máx 50 MB.")

    parts = [_slugify(collection_slug)]
    if box and box.strip():
        parts.append(_slugify(box, 40))
    if subdivision and subdivision.strip():
        parts.append(_slugify(subdivision, 40))

    dest_dir = Path("storage/images").joinpath(*parts)
    dest_dir.mkdir(parents=True, exist_ok=True)

    unique = f"{uuid.uuid4().hex[:8]}_{_safe_filename(file.filename or 'photo.jpg')}"
    (dest_dir / unique).write_bytes(content)

    relative = "/".join(["images"] + parts + [unique])
    return relative, size


# ── Schemas ────────────────────────────────────────────────────────────────────

class UploadedImageResponse(PydanticModel):
    id: int
    title: str
    file_path: str
    year: Optional[int]
    location: Optional[str]
    collection_id: Optional[int]
    is_public: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class BulkUploadResult(PydanticModel):
    filename: str
    ok: bool
    image_id: Optional[int] = None
    error: Optional[str] = None


class BulkUploadResponse(PydanticModel):
    total: int
    succeeded: int
    failed: int
    results: List[BulkUploadResult]


# ── Upload: single ────────────────────────────────────────────────────────────

@router.post(
    "/upload/single",
    response_model=UploadedImageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_single(
    file: UploadFile = File(...),
    collection_id: int = Form(...),
    title: str = Form(""),
    year: Optional[int] = Form(None),
    location: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    is_public: bool = Form(True),
    box: Optional[str] = Form(None),
    subdivision: Optional[str] = Form(None),
    user_id: int = Depends(_require_write_access),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a single photograph and create an ImageModel record for the viewer.
    Accepts multipart/form-data with the file + metadata fields.
    """
    from app.features.view_images.infrastructure.persistence.image_model import ImageModel
    from app.features.view_images.infrastructure.persistence.image_model import CollectionModel

    # Verify collection exists and get slug
    col_res = await db.execute(
        sa_select(CollectionModel).where(CollectionModel.id == collection_id)
    )
    col = col_res.scalar_one_or_none()
    if not col:
        raise HTTPException(status_code=404, detail="Colección no encontrada.")

    slug = col.slug or _slugify(col.name.lower())
    rel_path, size = await _save_upload(file, slug, box=box, subdivision=subdivision)

    effective_title = title.strip() or _safe_filename(file.filename or "sin_titulo.jpg")

    img = ImageModel(
        title=effective_title,
        file_path=f"/storage/{rel_path}",
        description=description or None,
        year=year,
        location=location or None,
        author="Robert Gerstmann",
        tags=[],
        collection_id=collection_id,
        image_metadata={"file_size_bytes": size},
        is_public=is_public,
    )
    db.add(img)
    await db.flush()
    await db.refresh(img)

    return UploadedImageResponse(
        id=img.id,
        title=img.title,
        file_path=img.file_path,
        year=img.year,
        location=img.location,
        collection_id=img.collection_id,
        is_public=img.is_public,
        created_at=img.created_at,
    )


# ── Upload: bulk ──────────────────────────────────────────────────────────────

@router.post("/upload/bulk", response_model=BulkUploadResponse)
async def upload_bulk(
    files: List[UploadFile] = File(...),
    collection_id: int = Form(...),
    year: Optional[int] = Form(None),
    location: Optional[str] = Form(None),
    is_public: bool = Form(True),
    box: Optional[str] = Form(None),
    subdivision: Optional[str] = Form(None),
    user_id: int = Depends(_require_write_access),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload multiple photographs at once.
    All files share the same collection, year, and location defaults.
    Returns per-file results so the client can show individual success/errors.
    """
    from app.features.view_images.infrastructure.persistence.image_model import ImageModel
    from app.features.view_images.infrastructure.persistence.image_model import CollectionModel

    col_res = await db.execute(
        sa_select(CollectionModel).where(CollectionModel.id == collection_id)
    )
    col = col_res.scalar_one_or_none()
    if not col:
        raise HTTPException(status_code=404, detail="Colección no encontrada.")

    slug = col.slug or _slugify(col.name.lower())
    results: List[BulkUploadResult] = []

    for upload in files:
        fname = upload.filename or "photo.jpg"
        try:
            rel_path, size = await _save_upload(upload, slug, box=box, subdivision=subdivision)
            img = ImageModel(
                title=_safe_filename(fname),
                file_path=f"/storage/{rel_path}",
                year=year,
                location=location or None,
                author="Robert Gerstmann",
                tags=[],
                collection_id=collection_id,
                image_metadata={"file_size_bytes": size},
                is_public=is_public,
            )
            db.add(img)
            await db.flush()
            await db.refresh(img)
            results.append(BulkUploadResult(filename=fname, ok=True, image_id=img.id))
        except HTTPException as e:
            results.append(BulkUploadResult(filename=fname, ok=False, error=e.detail))
        except Exception as e:
            results.append(BulkUploadResult(filename=fname, ok=False, error=str(e)))

    succeeded = sum(1 for r in results if r.ok)
    return BulkUploadResponse(
        total=len(results),
        succeeded=succeeded,
        failed=len(results) - succeeded,
        results=results,
    )


# ── Collection cover ──────────────────────────────────────────────────────────

@router.post("/collections/{collection_id}/cover", response_model=CollectionResponse)
async def set_collection_cover(
    collection_id: int,
    file: Optional[UploadFile] = File(None),
    image_path: Optional[str] = Form(None),
    user_id: int = Depends(_require_write_access),
    db: AsyncSession = Depends(get_db),
):
    """
    Set the cover image for a collection.
    Accepts either a file upload OR the path of an existing image already in storage.
    """
    from app.features.view_images.infrastructure.persistence.image_model import CollectionModel

    col_res = await db.execute(
        sa_select(CollectionModel).where(CollectionModel.id == collection_id)
    )
    col = col_res.scalar_one_or_none()
    if not col:
        raise HTTPException(status_code=404, detail="Colección no encontrada.")

    if file and file.filename:
        slug = col.slug or re.sub(r"[^\w\-]", "_", col.name.lower())[:60]
        rel_path, _ = await _save_upload(file, f"{slug}/covers")
        cover_path = f"/storage/{rel_path}"
    elif image_path:
        cover_path = image_path
    else:
        raise HTTPException(status_code=400, detail="Se requiere un archivo o una ruta de imagen existente.")

    col.cover_image_path = cover_path
    await db.flush()
    await db.refresh(col)

    return CollectionResponse(
        id=col.id,
        name=col.name,
        slug=col.slug,
        description=col.description,
        photographer_name=col.photographer_name,
        origin_country=col.origin_country,
        date_range_from=col.date_range_from,
        date_range_to=col.date_range_to,
        is_public=col.is_public,
        cover_image_path=col.cover_image_path,
        license=col.license,
        copyright_notes=col.copyright_notes,
        created_by=col.created_by,
        created_at=col.created_at,
        updated_at=col.updated_at,
    )
