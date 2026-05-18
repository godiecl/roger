from datetime import datetime
from sqlalchemy import Column, Integer, Text, String, Boolean, DateTime, ForeignKey
from app.infrastructure.database.base import Base


class ImageContextModel(Base):
    __tablename__ = "image_contexts"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, nullable=False, index=True)
    text = Column(Text, nullable=False)
    provider = Column(String(50), nullable=False)
    generation_time_ms = Column(Integer, nullable=False, default=0)

    is_anchored = Column(Boolean, default=False, nullable=False, index=True)
    anchored_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    anchored_at = Column(DateTime, nullable=True)

    like_count = Column(Integer, default=0, nullable=False)
    report_count = Column(Integer, default=0, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<ImageContextModel(id={self.id}, image_id={self.image_id}, anchored={self.is_anchored})>"
