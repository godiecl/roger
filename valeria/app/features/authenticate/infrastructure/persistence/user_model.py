"""
User SQLAlchemy model for ROGER - Valeria API
"""

from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum

from app.infrastructure.database.base import BaseModel
from app.features.authenticate.domain.role import Role


class UserModel(BaseModel):
    """SQLAlchemy model for User table."""

    __tablename__ = "users"

    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(
        SQLEnum(Role, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=Role.COLABORADOR,
    )
    full_name = Column(String, nullable=True)
    first_name = Column(String(150), nullable=True)
    last_name = Column(String(150), nullable=True)
    company = Column(String, nullable=True)
    rut_passport = Column(String(30), nullable=True)
    phone = Column(String(30), nullable=True)
    nationality = Column(String(100), nullable=True)
    gender = Column(String(50), nullable=True)
    affiliation = Column(String(255), nullable=True)
    organization = Column(String(255), nullable=True)
    position = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    expiry_date = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<UserModel(id={self.id}, email={self.email}, role={self.role})>"
