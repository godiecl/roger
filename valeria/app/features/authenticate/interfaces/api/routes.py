"""
FastAPI routes for authentication
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.authenticate.interfaces.api.schemas import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    UserResponse
)
from app.features.authenticate.application.authenticate_usecase import (
    AuthenticateUseCase
)
from app.features.authenticate.infrastructure.adapters.user_repository import (
    UserRepository
)
from app.features.authenticate.infrastructure.adapters.password_hasher import (
    password_hasher
)
from app.features.authenticate.infrastructure.adapters.jwt_service import (
    jwt_service
)
from app.features.authenticate.domain.user import User
from app.features.authenticate.domain.role import Role
from app.infrastructure.database.session import get_db
from app.shared.domain.exceptions import UnauthorizedError


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Login endpoint.
    
    Returns access token and refresh token.
    """
    try:
        # Create use case
        user_repository = UserRepository(db)
        authenticate_usecase = AuthenticateUseCase(
            user_repository,
            password_hasher,
            jwt_service
        )
        
        # Execute use case
        result = await authenticate_usecase.execute(
            email=request.email,
            password=request.password
        )
        
        return result
        
    except UnauthorizedError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user.
    
    Only allows public roles (USUARIO_ESTANDAR, COLABORADOR).
    """
    # Validate role
    if request.role not in Role.get_public_roles():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot register with this role"
        )
    
    # Create user repository
    user_repository = UserRepository(db)
    
    # Check if user exists
    existing_user = await user_repository.get_by_email(request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create user
    user = User(
        email=request.email,
        hashed_password=password_hasher.hash(request.password),
        role=request.role,
        full_name=request.full_name,
        is_active=True,
        is_verified=False
    )
    
    # Save user
    created_user = await user_repository.create(user)
    
    return UserResponse(
        id=created_user.id,
        email=created_user.email,
        role=created_user.role,
        full_name=created_user.full_name,
        is_active=created_user.is_active,
        is_verified=created_user.is_verified
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    # TODO: Add authentication dependency
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user information.
    
    Requires authentication.
    """
    # TODO: Implement with authentication dependency
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not implemented yet"
    )
