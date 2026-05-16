from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Enum as SQLEnum

from app.infrastructure.database.base import BaseModel
from app.features.generate_timeline.domain.timeline import (
    EventType, SourceType, TimelineAxis,
)


def _enum_values(x):
    return [e.value for e in x]


class TimelineModel(BaseModel):
    """Línea de tiempo generada para una fotografía."""

    __tablename__ = "timelines"

    photograph_id = Column(
        Integer, ForeignKey("photographs.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    provider = Column(String(150), nullable=False)
    context_summary = Column(Text, nullable=True)
    generation_time_ms = Column(Integer, nullable=True)
    is_approved = Column(Boolean, nullable=False, default=False)
    approved_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<TimelineModel(id={self.id}, photograph_id={self.photograph_id}, approved={self.is_approved})>"


class TimelineEventModel(BaseModel):
    """Evento individual dentro de una línea de tiempo."""

    __tablename__ = "timeline_events"

    timeline_id = Column(
        Integer, ForeignKey("timelines.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    date_label = Column(String(100), nullable=False)
    year = Column(Integer, nullable=True, index=True)
    title = Column(String(512), nullable=False)
    description = Column(Text, nullable=False)
    axis = Column(
        SQLEnum(TimelineAxis, values_callable=_enum_values),
        nullable=False,
    )
    event_type = Column(
        SQLEnum(EventType, values_callable=_enum_values),
        nullable=False,
        default=EventType.OTHER,
    )
    source_type = Column(
        SQLEnum(SourceType, values_callable=_enum_values),
        nullable=False,
        default=SourceType.VEROSIMIL,
    )

    def __repr__(self) -> str:
        return f"<TimelineEventModel(id={self.id}, date={self.date_label}, title={self.title[:40]})>"
