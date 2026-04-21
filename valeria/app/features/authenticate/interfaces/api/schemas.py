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
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None
    company: Optional[str] = Field(None, max_length=255)
    role: Role = Role.USUARIO_ESTANDAR
    verification_token: str
    verification_code: str = Field(..., min_length=6, max_length=6)


class UserResponse(BaseModel):
    """User response schema."""
    id: int
    email: str
    username: str
    role: Role
    full_name: Optional[str]
    company: Optional[str]
    is_active: bool
    is_verified: bool
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str = "bearer"


class SendVerificationCodeRequest(BaseModel):
    """Request to send email verification code."""
    email: EmailStr


class SendVerificationCodeResponse(BaseModel):
    """Response after sending verification code."""
    token: str
    message: str


class ForgotPasswordRequest(BaseModel):
    """Forgot password request schema."""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Reset password request schema."""
    token: str
    new_password: str = Field(..., min_length=8)


class ChangePasswordRequest(BaseModel):
    """Change password request for authenticated users."""
    current_password: str
    new_password: str = Field(..., min_length=8)


class UpdateProfileRequest(BaseModel):
    """Update profile request for authenticated users."""
    full_name: Optional[str] = Field(None, max_length=255)
    company: Optional[str] = Field(None, max_length=255)


class UserAdminResponse(BaseModel):
    """User info for admin panel."""
    id: int
    email: str
    username: str
    full_name: Optional[str]
    company: Optional[str]
    role: Role
    is_active: bool
    is_verified: bool

    class Config:
        from_attributes = True


class UserAdminListResponse(BaseModel):
    """List of users for admin panel."""
    total: int
    users: list[UserAdminResponse]


class RequestEmailChangeRequest(BaseModel):
    """Request to change the authenticated user's email."""
    new_email: EmailStr


class AdminCreateUserRequest(BaseModel):
    """Admin: create a new user."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)
    company: Optional[str] = Field(None, max_length=255)
    role: Role = Role.USUARIO_ESTANDAR
    password: str = Field(..., min_length=8)


class ContactRequest(BaseModel):
    """Contact form submission."""
    name: str = Field(..., min_length=2, max_length=200)
    email: EmailStr
    company: Optional[str] = Field(None, max_length=255)
    subject: str = Field(..., min_length=2, max_length=200)
    message: str = Field(..., min_length=10, max_length=3000)


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str


class UserSearchResult(BaseModel):
    """Minimal user info for email autocomplete."""
    id: int
    email: str
    full_name: Optional[str]

    class Config:
        from_attributes = True
