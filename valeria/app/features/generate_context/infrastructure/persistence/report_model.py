from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, UniqueConstraint
from app.infrastructure.database.base import Base


class ContentReportModel(Base):
    __tablename__ = "content_reports"

    id = Column(Integer, primary_key=True, index=True)
    content_type = Column(String(20), nullable=False)   # 'context' | 'narrative'
    content_id = Column(Integer, nullable=False)
    ip_hash = Column(String(64), nullable=False)        # SHA256 of IP, never raw IP
    reason = Column(Text, nullable=True)
    status = Column(String(20), default="pending", nullable=False, index=True)  # pending|reviewed|dismissed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("content_type", "content_id", "ip_hash", name="uq_content_report"),
    )

    def __repr__(self):
        return f"<ContentReportModel({self.content_type}:{self.content_id}, status={self.status})>"
