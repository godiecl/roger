"""
FastAPI routes for the archive feature.
Manages the physical hierarchy: Box → Roll → Photograph → PhotographFile.
Write operations require CURADOR or ADMINISTRADOR role.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

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
    BoxCreateRequest, BoxListResponse, BoxResponse,
    RollCreateRequest, RollListResponse, RollResponse,
    PhotographCreateRequest, PhotographListResponse, PhotographResponse,
    PhotographFileCreateRequest, PhotographFileListResponse, PhotographFileResponse,
)
from app.features.authenticate.domain.role import Role
from app.features.authenticate.infrastructure.adapters.user_repository import UserRepository
from app.features.authenticate.interfaces.api.dependencies import get_current_user_id
from app.infrastructure.database.session import get_db
from app.shared.domain.exceptions import EntityNotFoundError, ValidationError


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

@router.post(
    "/photographs/{photograph_id}/files",
    response_model=PhotographFileResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_file(
    photograph_id: int,
    request: PhotographFileCreateRequest,
    _: int = Depends(_require_write_access),
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
        return PhotographFileResponse(**pf.__dict__)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


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
