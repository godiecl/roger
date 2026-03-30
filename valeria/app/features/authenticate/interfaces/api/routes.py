"""
FastAPI routes for authentication
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.authenticate.interfaces.api.schemas import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    UserResponse,
    UserSearchResult,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    MessageResponse,
    SendVerificationCodeRequest,
    SendVerificationCodeResponse,
)
from app.infrastructure.email.email_service import email_service
from app.config.settings import settings
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
from app.features.authenticate.interfaces.api.dependencies import get_current_user_id
from app.infrastructure.database.session import get_db
from app.shared.domain.exceptions import UnauthorizedError
import secrets


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


@router.post("/send-verification-code", response_model=SendVerificationCodeResponse)
async def send_verification_code(request: SendVerificationCodeRequest):
    """
    Send a 6-digit verification code to the given email.

    Returns a signed token that must be submitted alongside the code during registration.
    Always responds with 200 to avoid leaking whether an email is already registered.
    """
    code = "".join(str(secrets.randbelow(10)) for _ in range(6))
    code_hash = password_hasher.hash(code)
    token = jwt_service.create_email_verification_token(request.email, code_hash)

    try:
        email_service.send_verification_code(request.email, code)
    except Exception:
        pass

    return SendVerificationCodeResponse(
        token=token,
        message="Si el correo es válido, recibirás un código de verificación en breve."
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user.

    Requires a valid verification_token and verification_code obtained from
    POST /auth/send-verification-code.
    Only allows public roles (USUARIO_ESTANDAR, COLABORADOR).
    """
    # Validate verification token and code
    try:
        payload = jwt_service.decode_email_verification_token(request.verification_token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El token de verificación es inválido o ha expirado."
        )

    token_email: str = payload.get("sub", "")
    code_hash: str = payload.get("code_hash", "")

    if token_email.lower() != request.email.lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo no coincide con el token de verificación."
        )

    if not password_hasher.verify(request.verification_code, code_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El código de verificación es incorrecto."
        )

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

    # Create user (mark as verified since they confirmed their email)
    user = User(
        email=request.email,
        username=request.username,
        hashed_password=password_hasher.hash(request.password),
        role=request.role,
        full_name=request.full_name,
        is_active=True,
        is_verified=True
    )

    created_user = await user_repository.create(user)

    return UserResponse(
        id=created_user.id,
        email=created_user.email,
        username=created_user.username,
        role=created_user.role,
        full_name=created_user.full_name,
        is_active=created_user.is_active,
        is_verified=created_user.is_verified
    )


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    request: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Request a password reset email.

    Always returns 200 to avoid leaking whether an email is registered.
    """
    user_repository = UserRepository(db)
    user = await user_repository.get_by_email(request.email)

    if user and user.is_active:
        token = jwt_service.create_reset_token(user.id, user.email)
        reset_url = f"{settings.frontend_url}/reset-password?token={token}"
        try:
            email_service.send_password_reset(user.email, reset_url)
        except Exception:
            # Log but don't expose SMTP errors to the client
            pass

    return MessageResponse(
        message="Si el correo está registrado, recibirás un enlace para restablecer tu contraseña."
    )


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Reset password using the token received by email.
    """
    try:
        payload = jwt_service.decode_reset_token(request.token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El enlace es inválido o ha expirado. Solicita uno nuevo."
        )

    user_id: int = payload.get("user_id")
    user_repository = UserRepository(db)
    user = await user_repository.get_by_id(user_id)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El enlace es inválido o ha expirado."
        )

    user.hashed_password = password_hasher.hash(request.new_password)
    await user_repository.update(user)

    return MessageResponse(message="Contraseña actualizada correctamente.")


@router.get("/users/search", response_model=list[UserSearchResult])
async def search_users(
    q: str = Query(..., min_length=1),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Search users by email for autocomplete. Requires authentication."""
    user_repository = UserRepository(db)
    users = await user_repository.search_by_email(q)
    return [UserSearchResult(id=u.id, email=u.email, full_name=u.full_name) for u in users]


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user information.

    Requires authentication.
    """
    user_repository = UserRepository(db)
    user = await user_repository.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        role=user.role,
        full_name=user.full_name,
        is_active=user.is_active,
        is_verified=user.is_verified
    )
