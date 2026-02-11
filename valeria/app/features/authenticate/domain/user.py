"""
User entity for ROGER - Valeria API
"""

from datetime import datetime
from typing import Optional

from app.shared.domain.base_entity import BaseEntity
from app.features.authenticate.domain.role import Role


class User(BaseEntity):
    """
    User domain entity.
    Represents a user in the ROGER system.
    """
    
    def __init__(
        self,
        email: str,
        hashed_password: str,
        role: Role,
        full_name: Optional[str] = None,
        is_active: bool = True,
        is_verified: bool = False,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        super().__init__(id, created_at, updated_at)
        self.email = email
        self.hashed_password = hashed_password
        self.role = role
        self.full_name = full_name
        self.is_active = is_active
        self.is_verified = is_verified
    
    def can_create_narratives(self) -> bool:
        """Check if user can create narratives."""
        return Role.can_create_narratives(self.role)
    
    def can_moderate(self) -> bool:
        """Check if user can moderate content."""
        return Role.can_moderate(self.role)
    
    def is_admin(self) -> bool:
        """Check if user is an administrator."""
        return self.role == Role.ADMINISTRADOR
    
    def activate(self) -> None:
        """Activate user account."""
        self.is_active = True
        self.updated_at = datetime.utcnow()
    
    def deactivate(self) -> None:
        """Deactivate user account."""
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def verify(self) -> None:
        """Verify user email."""
        self.is_verified = True
        self.updated_at = datetime.utcnow()
    
    def __repr__(self) -> str:
        return f"User(id={self.id}, email={self.email}, role={self.role})"
