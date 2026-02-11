"""
Pydantic schemas for authentication API
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional

from app.features.authenticate.domain.role import Role


class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str = Field(..., min_length=6)


class LoginResponse(BaseModel):
    """Login response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class RegisterRequest(BaseModel):
    """Register request schema."""
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None
    role: Role = Role.USUARIO_ESTANDAR


class UserResponse(BaseModel):
    """User response schema."""
    id: int
    email: str
    role: Role
    full_name: Optional[str]
    is_active: bool
    is_verified: bool
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str = "bearer"
