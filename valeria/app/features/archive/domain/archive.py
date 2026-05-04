"""
Archive domain entities for ROGER - Valeria API.
Box → Roll → Photograph → PhotographFile physical hierarchy.
"""

from datetime import datetime, date
from enum import Enum
from typing import Optional

from app.shared.domain.base_entity import BaseEntity


class ImageType(str, Enum):
    NEG = "neg"
    POS = "pos"


class SupportType(str, Enum):
    PAPER = "paper"
    GLASS = "glass"
    FLEX = "flex"


class PhysicalStatus(str, Enum):
    GOOD = "good"
    INTER = "inter"
    BAD = "bad"


class ColorMode(str, Enum):
    BW = "bw"
    COLOR = "color"


class FileType(str, Enum):
    CR3 = "cr3"
    TIFF = "tiff"
    JPG = "jpg"
    PNG = "png"


class Box(BaseEntity):
    """Physical storage box within a collection."""

    def __init__(
        self,
        collection_id: int,
        box_number: int,
        name: Optional[str] = None,
        location_in_archive: Optional[str] = None,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        super().__init__(id, created_at, updated_at)
        self.collection_id = collection_id
        self.box_number = box_number
        self.name = name
        self.location_in_archive = location_in_archive

    def __repr__(self) -> str:
        return f"Box(id={self.id}, box_number={self.box_number})"


class Roll(BaseEntity):
    """Individual 35mm film roll within a box."""

    def __init__(
        self,
        box_id: int,
        general_number: Optional[int] = None,
        internal_number: Optional[int] = None,
        og_number: Optional[int] = None,
        strip_letter: Optional[str] = None,
        name: Optional[str] = None,
        image_type: Optional[ImageType] = None,
        support: Optional[SupportType] = None,
        physical_status: Optional[PhysicalStatus] = None,
        color_mode: Optional[ColorMode] = None,
        frame_count: Optional[int] = None,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        super().__init__(id, created_at, updated_at)
        self.box_id = box_id
        self.general_number = general_number
        self.internal_number = internal_number
        self.og_number = og_number
        self.strip_letter = strip_letter
        self.name = name
        self.image_type = image_type
        self.support = support
        self.physical_status = physical_status
        self.color_mode = color_mode
        self.frame_count = frame_count

    def __repr__(self) -> str:
        return f"Roll(id={self.id}, general_number={self.general_number})"


class Photograph(BaseEntity):
    """Individual photographic frame within a roll."""

    def __init__(
        self,
        roll_id: int,
        frame_number: Optional[int] = None,
        identifier: Optional[str] = None,
        physical_location_ref: Optional[str] = None,
        digitalization_date: Optional[date] = None,
        width_px: Optional[int] = None,
        height_px: Optional[int] = None,
        color_depth: Optional[int] = None,
        resolution_dpi: Optional[float] = None,
        internal_cronology: Optional[str] = None,
        license: Optional[str] = None,
        copyright_notes: Optional[str] = None,
        is_public: bool = True,
        digitalized_by: Optional[int] = None,
        responsible_by: Optional[int] = None,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        super().__init__(id, created_at, updated_at)
        self.roll_id = roll_id
        self.frame_number = frame_number
        self.identifier = identifier
        self.physical_location_ref = physical_location_ref
        self.digitalization_date = digitalization_date
        self.width_px = width_px
        self.height_px = height_px
        self.color_depth = color_depth
        self.resolution_dpi = resolution_dpi
        self.internal_cronology = internal_cronology
        self.license = license
        self.copyright_notes = copyright_notes
        self.is_public = is_public
        self.digitalized_by = digitalized_by
        self.responsible_by = responsible_by

    def __repr__(self) -> str:
        return f"Photograph(id={self.id}, roll_id={self.roll_id}, frame={self.frame_number})"


class PhotographFile(BaseEntity):
    """Physical file associated with a photograph (master CR3 + derivatives)."""

    def __init__(
        self,
        photograph_id: int,
        file_type: FileType,
        file_path: str,
        is_master: bool = False,
        file_size_bytes: Optional[int] = None,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        super().__init__(id, created_at, updated_at)
        self.photograph_id = photograph_id
        self.file_type = file_type
        self.file_path = file_path
        self.is_master = is_master
        self.file_size_bytes = file_size_bytes

    def __repr__(self) -> str:
        return f"PhotographFile(id={self.id}, file_type={self.file_type}, is_master={self.is_master})"
