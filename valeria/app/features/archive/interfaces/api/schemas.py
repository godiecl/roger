"""
Pydantic schemas for the archive feature API.
"""

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.features.archive.domain.archive import ColorMode, FileType, ImageType, PhysicalStatus, SupportType


# ── Collection ────────────────────────────────────────────────────────────────

class CollectionCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    photographer_name: Optional[str] = None
    origin_country: Optional[str] = None
    date_range_from: Optional[int] = Field(None, ge=1800, le=2100)
    date_range_to: Optional[int] = Field(None, ge=1800, le=2100)
    is_public: bool = True
    cover_image_path: Optional[str] = None
    license: Optional[str] = None
    copyright_notes: Optional[str] = None


class CollectionUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    photographer_name: Optional[str] = None
    origin_country: Optional[str] = None
    date_range_from: Optional[int] = Field(None, ge=1800, le=2100)
    date_range_to: Optional[int] = Field(None, ge=1800, le=2100)
    is_public: Optional[bool] = None
    cover_image_path: Optional[str] = None
    license: Optional[str] = None
    copyright_notes: Optional[str] = None


class CollectionResponse(BaseModel):
    id: int
    name: str
    slug: Optional[str]
    description: Optional[str]
    photographer_name: Optional[str]
    origin_country: Optional[str]
    date_range_from: Optional[int]
    date_range_to: Optional[int]
    is_public: bool
    cover_image_path: Optional[str]
    license: Optional[str]
    copyright_notes: Optional[str]
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CollectionListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    collections: List[CollectionResponse]


# ── Box ───────────────────────────────────────────────────────────────────────

class BoxCreateRequest(BaseModel):
    collection_id: int
    box_number: int = Field(..., ge=1)
    name: Optional[str] = None
    location_in_archive: Optional[str] = None


class BoxResponse(BaseModel):
    id: int
    collection_id: int
    box_number: int
    name: Optional[str]
    location_in_archive: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BoxListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    boxes: List[BoxResponse]


# ── Roll ──────────────────────────────────────────────────────────────────────

class RollCreateRequest(BaseModel):
    box_id: int
    general_number: Optional[int] = None
    internal_number: Optional[int] = None
    og_number: Optional[int] = None
    strip_letter: Optional[str] = None
    name: Optional[str] = None
    image_type: Optional[ImageType] = None
    support: Optional[SupportType] = None
    physical_status: Optional[PhysicalStatus] = None
    color_mode: Optional[ColorMode] = None
    frame_count: Optional[int] = None


class RollResponse(BaseModel):
    id: int
    box_id: int
    general_number: Optional[int]
    internal_number: Optional[int]
    og_number: Optional[int]
    strip_letter: Optional[str]
    name: Optional[str]
    image_type: Optional[ImageType]
    support: Optional[SupportType]
    physical_status: Optional[PhysicalStatus]
    color_mode: Optional[ColorMode]
    frame_count: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RollListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    rolls: List[RollResponse]


# ── Photograph ────────────────────────────────────────────────────────────────

class PhotographCreateRequest(BaseModel):
    roll_id: int
    frame_number: Optional[int] = None
    identifier: Optional[str] = None
    physical_location_ref: Optional[str] = None
    digitalization_date: Optional[date] = None
    width_px: Optional[int] = None
    height_px: Optional[int] = None
    color_depth: Optional[int] = None
    resolution_dpi: Optional[float] = None
    internal_cronology: Optional[str] = None
    license: Optional[str] = None
    copyright_notes: Optional[str] = None
    is_public: bool = True
    digitalized_by: Optional[int] = None
    responsible_by: Optional[int] = None


class PhotographResponse(BaseModel):
    id: int
    roll_id: int
    frame_number: Optional[int]
    identifier: Optional[str]
    physical_location_ref: Optional[str]
    digitalization_date: Optional[date]
    width_px: Optional[int]
    height_px: Optional[int]
    color_depth: Optional[int]
    resolution_dpi: Optional[float]
    internal_cronology: Optional[str]
    license: Optional[str]
    copyright_notes: Optional[str]
    is_public: bool
    digitalized_by: Optional[int]
    responsible_by: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PhotographListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    photographs: List[PhotographResponse]


# ── PhotographFile ────────────────────────────────────────────────────────────

class PhotographFileCreateRequest(BaseModel):
    file_type: FileType
    file_path: str = Field(..., min_length=1)
    is_master: bool = False
    file_size_bytes: Optional[int] = None


class PhotographFileResponse(BaseModel):
    id: int
    photograph_id: int
    file_type: FileType
    file_path: str
    is_master: bool
    file_size_bytes: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PhotographFileListResponse(BaseModel):
    total: int
    files: List[PhotographFileResponse]
