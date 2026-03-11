"""
ProjectInvitation SQLAlchemy model for ROGER - Valeria API.
"""

from sqlalchemy import Column, String, Integer, ForeignKey, UniqueConstraint

from app.infrastructure.database.base import BaseModel


class ProjectInvitationModel(BaseModel):
    """SQLAlchemy model for project_invitations table."""

    __tablename__ = "project_invitations"

    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    invited_user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    invited_by_user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    status = Column(String(10), nullable=False, default='pending')

    __table_args__ = (
        UniqueConstraint("project_id", "invited_user_id", name="uq_project_invitation"),
    )

    def __repr__(self) -> str:
        return (
            f"<ProjectInvitationModel(id={self.id}, project_id={self.project_id}, "
            f"invited_user_id={self.invited_user_id}, status={self.status})>"
        )
