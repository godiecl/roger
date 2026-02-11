"""
User repository implementation for ROGER - Valeria API
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.features.authenticate.domain.user import User
from app.features.authenticate.domain.auth_port import IUserRepository
from app.features.authenticate.infrastructure.persistence.user_model import UserModel


class UserRepository(IUserRepository):
    """SQLAlchemy implementation of user repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, user: User) -> User:
        """Create a new user."""
        user_model = UserModel(
            email=user.email,
            hashed_password=user.hashed_password,
            role=user.role,
            full_name=user.full_name,
            is_active=user.is_active,
            is_verified=user.is_verified
        )
        
        self.session.add(user_model)
        await self.session.flush()
        await self.session.refresh(user_model)
        
        return self._to_entity(user_model)
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        user_model = result.scalar_one_or_none()
        
        return self._to_entity(user_model) if user_model else None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        user_model = result.scalar_one_or_none()
        
        return self._to_entity(user_model) if user_model else None
    
    async def update(self, user: User) -> User:
        """Update an existing user."""
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user.id)
        )
        user_model = result.scalar_one_or_none()
        
        if not user_model:
            raise ValueError(f"User with id {user.id} not found")
        
        user_model.email = user.email
        user_model.hashed_password = user.hashed_password
        user_model.role = user.role
        user_model.full_name = user.full_name
        user_model.is_active = user.is_active
        user_model.is_verified = user.is_verified
        
        await self.session.flush()
        await self.session.refresh(user_model)
        
        return self._to_entity(user_model)
    
    async def delete(self, user_id: int) -> bool:
        """Delete a user."""
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        user_model = result.scalar_one_or_none()
        
        if user_model:
            await self.session.delete(user_model)
            return True
        return False
    
    def _to_entity(self, model: UserModel) -> User:
        """Convert SQLAlchemy model to domain entity."""
        return User(
            id=model.id,
            email=model.email,
            hashed_password=model.hashed_password,
            role=model.role,
            full_name=model.full_name,
            is_active=model.is_active,
            is_verified=model.is_verified,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
