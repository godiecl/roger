"""
FastAPI routes for authentication
"""

import time

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

# ── Login rate limiter (IP + email, in-memory) ──────────────────────────────
_login_attempts: dict[str, dict] = {}
_LOGIN_MAX_ATTEMPTS = 5
_LOGIN_WINDOW_S     = 15 * 60   # 15 min window before counter resets
_LOGIN_BLOCK_S      = 30 * 60   # 30 min block after max attempts

def _login_key(ip: str, email: str) -> str:
    return f"{ip}:{email.lower().strip()}"

def _check_limit(key: str) -> tuple[bool, int]:
    """(allowed, seconds_blocked_remaining)"""
    now = time.time()
    rec = _login_attempts.get(key)
    if not rec:
        return True, 0
    blocked_until = rec.get("blocked_until", 0)
    if blocked_until and now < blocked_until:
        return False, int(blocked_until - now)
    if now - rec["first"] > _LOGIN_WINDOW_S:
        _login_attempts.pop(key, None)
        return True, 0
    if rec["count"] >= _LOGIN_MAX_ATTEMPTS:
        rec["blocked_until"] = now + _LOGIN_BLOCK_S
        return False, _LOGIN_BLOCK_S
    return True, 0

def _record_failure(key: str) -> int:
    now = time.time()
    if key not in _login_attempts:
        _login_attempts[key] = {"count": 0, "first": now}
    _login_attempts[key]["count"] += 1
    return _login_attempts[key]["count"]

def _reset_limit(key: str) -> None:
    _login_attempts.pop(key, None)

from app.features.authenticate.interfaces.api.schemas import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    UserResponse,
    UserSearchResult,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
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
    http_request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Login endpoint. Rate-limited by IP + email (5 attempts / 15 min)."""
    client_ip = http_request.client.host if http_request.client else "unknown"
    key = _login_key(client_ip, request.email)

    allowed, remaining = _check_limit(key)
    if not allowed:
        minutes = max(1, remaining // 60)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Demasiados intentos fallidos. Intenta de nuevo en {minutes} minuto{'s' if minutes != 1 else ''}."
        )

    try:
        user_repository = UserRepository(db)
        authenticate_usecase = AuthenticateUseCase(
            user_repository,
            password_hasher,
            jwt_service
        )
        result = await authenticate_usecase.execute(
            email=request.email,
            password=request.password
        )
        _reset_limit(key)
        return result

    except UnauthorizedError:
        count = _record_failure(key)
        left = _LOGIN_MAX_ATTEMPTS - count
        if left > 0:
            detail = f"Credenciales incorrectas. {left} intento{'s' if left != 1 else ''} restante{'s' if left != 1 else ''} antes del bloqueo."
        else:
            detail = "Cuenta bloqueada temporalmente. Intenta de nuevo en 30 minutos."
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail
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


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    request: ChangePasswordRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Change password for the currently authenticated user."""
    user_repository = UserRepository(db)
    user = await user_repository.get_by_id(user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    if not password_hasher.verify(request.current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña actual es incorrecta"
        )

    if request.current_password == request.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La nueva contraseña debe ser diferente a la actual"
        )

    user.hashed_password = password_hasher.hash(request.new_password)
    await user_repository.update(user)

    return MessageResponse(message="Contraseña actualizada correctamente")
