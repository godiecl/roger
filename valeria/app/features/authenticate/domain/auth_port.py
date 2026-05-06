"""
Authentication port (interface) for ROGER - Valeria API
"""

from abc import ABC, abstractmethod
from typing import Optional

from app.features.authenticate.domain.user import User


class IUserRepository(ABC):
    """Repository interface for User aggregate."""
    
    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a new user."""
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """Update an existing user."""
        pass
    
    @abstractmethod
    async def delete(self, user_id: int) -> bool:
        """Delete a user."""
        pass


class IPasswordHasher(ABC):
    """Password hasher interface."""
    
    @abstractmethod
    def hash(self, password: str) -> str:
        """Hash a password."""
        pass
    
    @abstractmethod
    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash."""
        pass


class IJWTService(ABC):
    """JWT service interface."""
    
    @abstractmethod
    def create_access_token(self, data: dict) -> str:
        """Create an access token."""
        pass
    
    @abstractmethod
    def create_refresh_token(self, data: dict) -> str:
        """Create a refresh token."""
        pass
    
    @abstractmethod
    def decode_token(self, token: str) -> dict:
        """Decode and verify a token."""
        pass
