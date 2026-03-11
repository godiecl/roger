"""
SQLAlchemy model for project messages.
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Index

from app.infrastructure.database.base import BaseModel


class ProjectMessageModel(BaseModel):
    """SQLAlchemy model for the project_messages table."""

    __tablename__ = "project_messages"

    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    content = Column(Text, nullable=False)
    message_type = Column(String(10), nullable=False, default='user')
    sender_name = Column(String(255), nullable=True)

    __table_args__ = (
        Index('ix_project_messages_project_created', 'project_id', 'created_at'),
    )
