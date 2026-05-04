"""
Archive SQLAlchemy models for ROGER - Valeria API
Boxes, Rolls, Photographs, PhotographFiles
"""

from enum import Enum

from sqlalchemy import (
    Column, String, Integer, Boolean, Text, Date, Float,
    ForeignKey, Enum as SQLEnum,
)

from app.infrastructure.database.base import BaseModel


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


class BoxModel(BaseModel):
    """Physical storage box within a collection."""

    __tablename__ = "boxes"

    collection_id = Column(
        Integer, ForeignKey("collections.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    box_number = Column(Integer, nullable=False)
    name = Column(String(255), nullable=True)
    location_in_archive = Column(String(255), nullable=True)

    def __repr__(self) -> str:
        return f"<BoxModel(id={self.id}, box_number={self.box_number})>"


class RollModel(BaseModel):
    """Individual 35mm film roll (Tira) within a box."""

    __tablename__ = "rolls"

    box_id = Column(
        Integer, ForeignKey("boxes.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    general_number = Column(Integer, nullable=True, index=True)
    internal_number = Column(Integer, nullable=True)
    og_number = Column(Integer, nullable=True)
    strip_letter = Column(String(5), nullable=True)
    name = Column(String(512), nullable=True)
    image_type = Column(
        SQLEnum(ImageType, values_callable=lambda x: [e.value for e in x]),
        nullable=True,
    )
    support = Column(
        SQLEnum(SupportType, values_callable=lambda x: [e.value for e in x]),
        nullable=True,
    )
    physical_status = Column(
        SQLEnum(PhysicalStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=True,
    )
    color_mode = Column(
        SQLEnum(ColorMode, values_callable=lambda x: [e.value for e in x]),
        nullable=True,
    )
    frame_count = Column(Integer, nullable=True)

    def __repr__(self) -> str:
        return f"<RollModel(id={self.id}, general_number={self.general_number}, name={self.name})>"


class PhotographModel(BaseModel):
    """Individual photographic frame within a roll."""

    __tablename__ = "photographs"

    roll_id = Column(
        Integer, ForeignKey("rolls.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    frame_number = Column(Integer, nullable=True)
    identifier = Column(String(100), nullable=True, index=True)
    physical_location_ref = Column(String(512), nullable=True)
    digitalization_date = Column(Date, nullable=True)
    width_px = Column(Integer, nullable=True)
    height_px = Column(Integer, nullable=True)
    color_depth = Column(Integer, nullable=True)
    resolution_dpi = Column(Float, nullable=True)
    internal_cronology = Column(String(255), nullable=True)
    license = Column(String(255), nullable=True)
    copyright_notes = Column(Text, nullable=True)
    is_public = Column(Boolean, default=True, nullable=False, index=True)
    digitalized_by = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True,
    )
    responsible_by = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True,
    )

    def __repr__(self) -> str:
        return f"<PhotographModel(id={self.id}, roll_id={self.roll_id}, frame={self.frame_number})>"


class PhotographFileModel(BaseModel):
    """Physical file associated with a photograph (master CR3 + derivatives)."""

    __tablename__ = "photograph_files"

    photograph_id = Column(
        Integer, ForeignKey("photographs.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    file_type = Column(
        SQLEnum(FileType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    file_path = Column(String(512), nullable=False)
    is_master = Column(Boolean, default=False, nullable=False)
    file_size_bytes = Column(Integer, nullable=True)

    def __repr__(self) -> str:
        return f"<PhotographFileModel(id={self.id}, file_type={self.file_type}, is_master={self.is_master})>"
