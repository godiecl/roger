"""
User SQLAlchemy model for ROGER - Valeria API
"""

from sqlalchemy import Column, String, Boolean, Enum as SQLEnum

from app.infrastructure.database.base import BaseModel
from app.features.authenticate.domain.role import Role


class UserModel(BaseModel):
    """SQLAlchemy model for User table."""

    __tablename__ = "users"

    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLEnum(Role), nullable=False, default=Role.USUARIO_ESTANDAR)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    def __repr__(self) -> str:
        return f"<UserModel(id={self.id}, email={self.email}, role={self.role})>"
