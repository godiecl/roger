"""
Project SQLAlchemy models for ROGER - Valeria API.
"""

from sqlalchemy import (
    Column, String, Text, Integer, Boolean, Date,
    ForeignKey, UniqueConstraint, Enum as SQLEnum
)

from app.infrastructure.database.base import BaseModel
from app.features.manage_projects.domain.project_role import ProjectRole


class ProjectModel(BaseModel):
    """SQLAlchemy model for projects table."""

    __tablename__ = "projects"

    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    owner_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    ai_instructions = Column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<ProjectModel(id={self.id}, name={self.name})>"


class ProjectMemberModel(BaseModel):
    """SQLAlchemy model for project_members table."""

    __tablename__ = "project_members"

    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    role = Column(
        SQLEnum(ProjectRole, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=ProjectRole.OBSERVADOR
    )

    __table_args__ = (
        UniqueConstraint("project_id", "user_id", name="uq_project_member"),
    )

    def __repr__(self) -> str:
        return (
            f"<ProjectMemberModel(id={self.id}, project_id={self.project_id}, "
            f"user_id={self.user_id}, role={self.role})>"
        )
