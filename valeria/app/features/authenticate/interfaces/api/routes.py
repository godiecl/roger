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
    UpdateProfileRequest,
    UserAdminResponse,
    UserAdminListResponse,
    RequestEmailChangeRequest,
    AdminCreateUserRequest,
    ContactRequest,
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
from app.shared.domain.exceptions import UnauthorizedError, InactiveAccountError
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

    except InactiveAccountError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu cuenta ha sido deshabilitada. Contacta al administrador para más información."
        )
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
        company=request.company,
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
        company=created_user.company,
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
        company=user.company,
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


@router.patch("/me", response_model=UserResponse)
async def update_profile(
    request: UpdateProfileRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Update the authenticated user's profile (full_name only)."""
    user_repository = UserRepository(db)
    user = await user_repository.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    if request.full_name is not None:
        user.full_name = request.full_name.strip() or None
    if request.company is not None:
        user.company = request.company.strip() or None

    user = await user_repository.update(user)
    return UserResponse(
        id=user.id, email=user.email, username=user.username,
        role=user.role, full_name=user.full_name, company=user.company,
        is_active=user.is_active, is_verified=user.is_verified
    )


# ── Admin endpoints ────────────────────────────────────────────────────────────

@router.get("/admin/users", response_model=UserAdminListResponse)
async def list_all_users(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """List all users. Admin only."""
    user_repository = UserRepository(db)
    requester = await user_repository.get_by_id(user_id)
    if not requester or requester.role.value != "administrador":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso restringido a administradores")

    users = await user_repository.list_all()
    return UserAdminListResponse(
        total=len(users),
        users=[UserAdminResponse(
            id=u.id, email=u.email, username=u.username,
            full_name=u.full_name, company=u.company, role=u.role,
            is_active=u.is_active, is_verified=u.is_verified
        ) for u in users]
    )


@router.patch("/admin/users/{target_id}/toggle-active", response_model=UserAdminResponse)
async def toggle_user_active(
    target_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Enable or disable a user account. Admin only."""
    user_repository = UserRepository(db)
    requester = await user_repository.get_by_id(user_id)
    if not requester or requester.role.value != "administrador":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso restringido a administradores")

    if target_id == user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No puedes modificar tu propia cuenta")

    target = await user_repository.get_by_id(target_id)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    target.is_active = not target.is_active
    target = await user_repository.update(target)
    return UserAdminResponse(
        id=target.id, email=target.email, username=target.username,
        full_name=target.full_name, company=target.company, role=target.role,
        is_active=target.is_active, is_verified=target.is_verified
    )


@router.patch("/admin/users/{target_id}/role", response_model=UserAdminResponse)
async def change_user_role(
    target_id: int,
    role: str,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Change a user's role. Admin only. Cannot change own role."""
    user_repository = UserRepository(db)
    requester = await user_repository.get_by_id(user_id)
    if not requester or requester.role.value != "administrador":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso restringido a administradores")

    if target_id == user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No puedes modificar tu propio rol")

    try:
        new_role = Role(role)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rol inválido")

    target = await user_repository.get_by_id(target_id)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    target.role = new_role
    target = await user_repository.update(target)
    return UserAdminResponse(
        id=target.id, email=target.email, username=target.username,
        full_name=target.full_name, company=target.company, role=target.role,
        is_active=target.is_active, is_verified=target.is_verified,
    )


@router.post("/admin/users", response_model=UserAdminResponse, status_code=status.HTTP_201_CREATED)
async def admin_create_user(
    request: AdminCreateUserRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Create a new user from the admin panel. Sends welcome email with credentials."""
    user_repository = UserRepository(db)
    requester = await user_repository.get_by_id(user_id)
    if not requester or requester.role.value != "administrador":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso restringido a administradores")

    existing = await user_repository.get_by_email(request.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe un usuario con ese correo")

    new_user = User(
        email=request.email,
        username=request.username,
        hashed_password=password_hasher.hash(request.password),
        role=request.role,
        full_name=request.full_name,
        company=request.company,
        is_active=True,
        is_verified=True,
    )
    created = await user_repository.create(new_user)

    try:
        email_service.send_welcome_email(
            to=created.email,
            full_name=created.full_name,
            username=created.username,
            password=request.password,
        )
    except Exception:
        pass

    return UserAdminResponse(
        id=created.id, email=created.email, username=created.username,
        full_name=created.full_name, company=created.company, role=created.role,
        is_active=created.is_active, is_verified=created.is_verified,
    )


# ── Email change endpoints ────────────────────────────────────────────────────

@router.post("/me/request-email-change", response_model=MessageResponse)
async def request_email_change(
    request: RequestEmailChangeRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Request an email address change. Sends confirmation link to the new address."""
    user_repository = UserRepository(db)
    user = await user_repository.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    if request.new_email.lower() == user.email.lower():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El nuevo correo debe ser diferente al actual")

    existing = await user_repository.get_by_email(request.new_email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ese correo ya está en uso")

    token = jwt_service.create_email_change_token(user_id, request.new_email)
    confirm_url = f"{settings.frontend_url}/confirm-email-change?token={token}"

    try:
        email_service.send_email_change_confirmation(to=request.new_email, confirm_url=confirm_url)
    except Exception:
        pass

    return MessageResponse(message="Se ha enviado un correo de confirmación a la nueva dirección. El enlace es válido por 30 minutos.")


@router.get("/me/confirm-email-change", response_model=MessageResponse)
async def confirm_email_change(
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """Confirm email change using the token received by email."""
    try:
        payload = jwt_service.decode_email_change_token(token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El enlace es inválido o ha expirado.")

    user_id = int(payload.get("sub"))
    new_email: str = payload.get("new_email")

    user_repository = UserRepository(db)

    existing = await user_repository.get_by_email(new_email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ese correo ya está en uso por otra cuenta.")

    user = await user_repository.get_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El enlace es inválido o ha expirado.")

    user.email = new_email
    await user_repository.update(user)

    return MessageResponse(message="Correo actualizado correctamente. Ya puedes iniciar sesión con tu nuevo correo.")


# ── Contact form ───────────────────────────────────────────────────────────────

@router.post("/contact", response_model=MessageResponse)
async def contact(request: ContactRequest):
    """Send a contact form message to the archive team."""
    company_line = f"<p><strong>Empresa / Institución:</strong> {request.company}</p>" if request.company else ""
    html = f"""
<!DOCTYPE html>
<html lang="es">
<head><meta charset="utf-8" /></head>
<body style="margin:0;padding:0;background:#f4f4f5;font-family:system-ui,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0">
    <tr>
      <td align="center" style="padding:40px 16px;">
        <table width="100%" style="max-width:520px;background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.08);">
          <tr>
            <td style="background:#1d1d1f;padding:28px 32px;text-align:center;">
              <p style="margin:0;font-size:22px;font-weight:700;color:#ffffff;letter-spacing:2px;">ROGER</p>
              <p style="margin:4px 0 0;font-size:11px;color:#888;text-transform:uppercase;letter-spacing:1px;">Nuevo mensaje de contacto</p>
            </td>
          </tr>
          <tr>
            <td style="padding:32px;">
              <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e5e7eb;border-radius:8px;overflow:hidden;">
                <tr style="background:#f9fafb;">
                  <td style="padding:10px 16px;font-size:12px;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:1px;width:120px;">Nombre</td>
                  <td style="padding:10px 16px;font-size:14px;color:#1d1d1f;">{request.name}</td>
                </tr>
                <tr>
                  <td style="padding:10px 16px;font-size:12px;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:1px;border-top:1px solid #e5e7eb;">Correo</td>
                  <td style="padding:10px 16px;font-size:14px;color:#2563eb;border-top:1px solid #e5e7eb;"><a href="mailto:{request.email}" style="color:#2563eb;">{request.email}</a></td>
                </tr>
                {"" if not request.company else f'''<tr style="background:#f9fafb;"><td style="padding:10px 16px;font-size:12px;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:1px;border-top:1px solid #e5e7eb;">Empresa</td><td style="padding:10px 16px;font-size:14px;color:#1d1d1f;border-top:1px solid #e5e7eb;">{request.company}</td></tr>'''}
                <tr {"" if not request.company else 'style=""'}>
                  <td style="padding:10px 16px;font-size:12px;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:1px;border-top:1px solid #e5e7eb;">Asunto</td>
                  <td style="padding:10px 16px;font-size:14px;color:#1d1d1f;border-top:1px solid #e5e7eb;">{request.subject}</td>
                </tr>
              </table>

              <div style="margin-top:24px;background:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;padding:16px 20px;">
                <p style="margin:0 0 8px;font-size:12px;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:1px;">Mensaje</p>
                <p style="margin:0;font-size:14px;color:#1d1d1f;line-height:1.7;white-space:pre-wrap;">{request.message}</p>
              </div>
            </td>
          </tr>
          <tr>
            <td style="padding:20px 32px;background:#f9f9f9;border-top:1px solid #eee;text-align:center;">
              <p style="margin:0;font-size:11px;color:#bbb;">
                Universidad Católica del Norte · Proyecto FONDEF ROGER<br />
                Este mensaje fue enviado desde el formulario de contacto público.
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
    """
    try:
        email_service.send(
            to=settings.smtp_from,
            subject=f"[ROGER Contacto] {request.subject} — {request.name}",
            html=html,
        )
    except Exception:
        pass

    return MessageResponse(message="Mensaje enviado correctamente. Te responderemos a la brevedad.")
