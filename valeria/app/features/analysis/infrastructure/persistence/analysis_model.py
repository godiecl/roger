"""
Analysis and Experiment SQLAlchemy models for ROGER - Valeria API
AnalysisJobs track tool executions; Experiments are formal research acts.
"""

from enum import Enum

from sqlalchemy import (
    Column, String, Integer, Text, DateTime,
    ForeignKey, Enum as SQLEnum, Date,
)
from sqlalchemy.sql import func

from app.infrastructure.database.base import Base


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ExperimentStatus(str, Enum):
    PLANNED = "planned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AnalysisAttributeType(str, Enum):
    TECHNICAL = "technical"
    CHRONOLOGY = "chronology"
    GEOGRAPHIC = "geographic"
    ENVIRONMENTAL = "environmental"


def _enum_values(x):
    return [e.value for e in x]


class AnalysisJobModel(Base):
    """
    Tracks every tool execution over a photograph.
    Agnostic to tool: tool_name is a free string (pillow, places365, geocLIP, claude, etc.).
    Linked optionally to an Experiment when it forms part of a formal research act.
    """

    __tablename__ = "analysis_jobs"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    photograph_id = Column(
        Integer, ForeignKey("photographs.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    attribute_type = Column(
        SQLEnum(AnalysisAttributeType, values_callable=_enum_values),
        nullable=False, index=True,
    )
    tool_name = Column(String(100), nullable=False)
    tool_version = Column(String(50), nullable=True)
    status = Column(
        SQLEnum(JobStatus, values_callable=_enum_values),
        nullable=False, default=JobStatus.PENDING, index=True,
    )
    triggered_by = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True,
    )
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return (
            f"<AnalysisJobModel(id={self.id}, photograph_id={self.photograph_id}, "
            f"tool={self.tool_name}, status={self.status})>"
        )


class ExperimentModel(Base):
    """
    Formal research act connecting a photograph, an attribute dimension,
    a researcher, a project, and the technical job that executed it.
    Captures the scientific intent behind each analysis run.
    """

    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    description = Column(Text, nullable=True)
    date = Column(Date, nullable=True)
    photograph_id = Column(
        Integer, ForeignKey("photographs.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    attribute_type = Column(
        SQLEnum(AnalysisAttributeType, values_callable=_enum_values),
        nullable=False,
    )
    conducted_by = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )
    project_id = Column(
        Integer, ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )
    analysis_job_id = Column(
        Integer, ForeignKey("analysis_jobs.id", ondelete="SET NULL"),
        nullable=True,
    )
    status = Column(
        SQLEnum(ExperimentStatus, values_callable=_enum_values),
        nullable=False, default=ExperimentStatus.PLANNED, index=True,
    )
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return (
            f"<ExperimentModel(id={self.id}, photograph_id={self.photograph_id}, "
            f"attribute_type={self.attribute_type}, status={self.status})>"
        )
