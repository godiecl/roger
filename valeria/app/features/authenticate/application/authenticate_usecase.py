"""
Authenticate use case for ROGER - Valeria API
"""

from typing import Dict
from app.features.authenticate.domain.auth_port import (
    IUserRepository,
    IPasswordHasher,
    IJWTService
)
from app.shared.domain.exceptions import UnauthorizedError


class AuthenticateUseCase:
    """
    Use case for user authentication.
    """
    
    def __init__(
        self,
        user_repository: IUserRepository,
        password_hasher: IPasswordHasher,
        jwt_service: IJWTService
    ):
        self.user_repository = user_repository
        self.password_hasher = password_hasher
        self.jwt_service = jwt_service
    
    async def execute(self, email: str, password: str) -> Dict[str, str]:
        """
        Authenticate a user and return tokens.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Dict with access_token and refresh_token
            
        Raises:
            UnauthorizedError: If credentials are invalid
        """
        # Get user by email
        user = await self.user_repository.get_by_email(email)
        
        if not user:
            raise UnauthorizedError("Invalid credentials")
        
        # Verify password
        if not self.password_hasher.verify(password, user.hashed_password):
            raise UnauthorizedError("Invalid credentials")
        
        # Check if user is active
        if not user.is_active:
            raise UnauthorizedError("User account is inactive")
        
        # Create tokens
        token_data = {
            "sub": user.email,
            "user_id": user.id,
            "role": user.role.value
        }
        
        access_token = self.jwt_service.create_access_token(token_data)
        refresh_token = self.jwt_service.create_refresh_token(token_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role.value,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "is_verified": user.is_verified
            }
        }
