"""
FastAPI routes for tag management in ROGER.

Tag vocabulary: CURADOR/ADMIN create and manage tags.
Photograph tagging: CURADOR/ADMIN assign/remove approved tags.
Any authenticated user can view tags.
"""

from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete

from app.features.authenticate.domain.role import Role
from app.features.authenticate.infrastructure.adapters.user_repository import UserRepository
from app.features.authenticate.interfaces.api.dependencies import get_current_user_id
from app.features.tagging.infrastructure.persistence.tag_model import (
    TagCategory, TagModel, TagSource, TagStatus, PhotographTagModel,
)
from app.infrastructure.database.session import get_db

router = APIRouter(prefix="/tags", tags=["Tags"])

_WRITE_ROLES = (Role.CURADOR, Role.ADMINISTRADOR)


async def _require_write(user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> int:
    user = await UserRepository(db).get_by_id(user_id)
    if not user or user.role not in _WRITE_ROLES:
        raise HTTPException(status_code=403, detail="Solo curadores y administradores pueden gestionar etiquetas.")
    return user_id


# ── Schemas ───────────────────────────────────────────────────────────────────

class TagCreateRequest(BaseModel):
    name: str
    category: TagCategory
    collection_id: Optional[int] = None


class TagResponse(BaseModel):
    id: int
    name: str
    category: TagCategory
    collection_id: Optional[int]
    created_at: datetime

    model_config = {"from_attributes": True}


class PhotographTagAddRequest(BaseModel):
    tag_id: int


class PhotographTagResponse(BaseModel):
    id: int
    photograph_id: int
    tag_id: int
    tag_name: str
    tag_category: TagCategory
    source: TagSource
    status: TagStatus
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    created_at: datetime


# ── Tag vocabulary CRUD ───────────────────────────────────────────────────────

@router.post("", response_model=TagResponse, status_code=201)
async def create_tag(
    request: TagCreateRequest,
    _: int = Depends(_require_write),
    db: AsyncSession = Depends(get_db),
):
    """Create a new tag in the controlled vocabulary."""
    existing = await db.execute(
        select(TagModel).where(TagModel.name == request.name, TagModel.collection_id == request.collection_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"Ya existe una etiqueta '{request.name}' en esta colección.")
    tag = TagModel(name=request.name, category=request.category, collection_id=request.collection_id)
    db.add(tag)
    await db.flush()
    await db.refresh(tag)
    return TagResponse(id=tag.id, name=tag.name, category=tag.category,
                       collection_id=tag.collection_id, created_at=tag.created_at)


@router.get("", response_model=List[TagResponse])
async def list_tags(
    category: Optional[TagCategory] = Query(None),
    collection_id: Optional[int] = Query(None),
    _: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """List all tags, optionally filtered by category or collection."""
    q = select(TagModel)
    if category:
        q = q.where(TagModel.category == category)
    if collection_id is not None:
        q = q.where(TagModel.collection_id == collection_id)
    q = q.order_by(TagModel.category, TagModel.name)
    result = await db.execute(q)
    tags = result.scalars().all()
    return [TagResponse(id=t.id, name=t.name, category=t.category,
                        collection_id=t.collection_id, created_at=t.created_at) for t in tags]


@router.delete("/{tag_id}", status_code=204)
async def delete_tag(
    tag_id: int,
    _: int = Depends(_require_write),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(TagModel).where(TagModel.id == tag_id))
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=404, detail="Etiqueta no encontrada.")
    await db.delete(tag)
    return None


# ── Photograph tagging ────────────────────────────────────────────────────────

@router.post("/photographs/{photograph_id}", response_model=PhotographTagResponse, status_code=201)
async def add_tag_to_photograph(
    photograph_id: int,
    request: PhotographTagAddRequest,
    user_id: int = Depends(_require_write),
    db: AsyncSession = Depends(get_db),
):
    """Assign a tag to a photograph (curator/admin, goes APPROVED immediately)."""
    tag_result = await db.execute(select(TagModel).where(TagModel.id == request.tag_id))
    tag = tag_result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=404, detail="Etiqueta no encontrada.")

    existing = await db.execute(
        select(PhotographTagModel).where(
            PhotographTagModel.photograph_id == photograph_id,
            PhotographTagModel.tag_id == request.tag_id,
            PhotographTagModel.source == TagSource.MANUAL,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Esta etiqueta ya está asignada a la fotografía.")

    pt = PhotographTagModel(
        photograph_id=photograph_id,
        tag_id=request.tag_id,
        source=TagSource.MANUAL,
        status=TagStatus.APPROVED,
        approved_by=user_id,
        approved_at=datetime.now(timezone.utc),
    )
    db.add(pt)
    await db.flush()
    await db.refresh(pt)
    return PhotographTagResponse(
        id=pt.id, photograph_id=pt.photograph_id, tag_id=pt.tag_id,
        tag_name=tag.name, tag_category=tag.category,
        source=pt.source, status=pt.status,
        approved_by=pt.approved_by, approved_at=pt.approved_at, created_at=pt.created_at,
    )


@router.get("/photographs/{photograph_id}", response_model=List[PhotographTagResponse])
async def list_photograph_tags(
    photograph_id: int,
    approved_only: bool = Query(True),
    _: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """List tags for a photograph."""
    q = select(PhotographTagModel, TagModel).join(TagModel, PhotographTagModel.tag_id == TagModel.id).where(
        PhotographTagModel.photograph_id == photograph_id
    )
    if approved_only:
        q = q.where(PhotographTagModel.status == TagStatus.APPROVED)
    result = await db.execute(q)
    rows = result.all()
    return [
        PhotographTagResponse(
            id=pt.id, photograph_id=pt.photograph_id, tag_id=pt.tag_id,
            tag_name=tag.name, tag_category=tag.category,
            source=pt.source, status=pt.status,
            approved_by=pt.approved_by, approved_at=pt.approved_at, created_at=pt.created_at,
        )
        for pt, tag in rows
    ]


@router.delete("/photographs/{photograph_id}/{tag_id}", status_code=204)
async def remove_tag_from_photograph(
    photograph_id: int,
    tag_id: int,
    _: int = Depends(_require_write),
    db: AsyncSession = Depends(get_db),
):
    """Remove a tag from a photograph."""
    result = await db.execute(
        select(PhotographTagModel).where(
            PhotographTagModel.photograph_id == photograph_id,
            PhotographTagModel.tag_id == tag_id,
        )
    )
    pt = result.scalar_one_or_none()
    if not pt:
        raise HTTPException(status_code=404, detail="Etiqueta no asignada a esta fotografía.")
    await db.delete(pt)
    return None
