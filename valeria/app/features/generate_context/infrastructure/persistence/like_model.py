from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint
from app.infrastructure.database.base import Base


class ContentLikeModel(Base):
    __tablename__ = "content_likes"

    id = Column(Integer, primary_key=True, index=True)
    content_type = Column(String(20), nullable=False)   # 'context' | 'narrative'
    content_id = Column(Integer, nullable=False)
    ip_hash = Column(String(64), nullable=False)        # SHA256 of IP, never raw IP
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("content_type", "content_id", "ip_hash", name="uq_content_like"),
    )

    def __repr__(self):
        return f"<ContentLikeModel({self.content_type}:{self.content_id}, ip={self.ip_hash[:8]}...)>"
