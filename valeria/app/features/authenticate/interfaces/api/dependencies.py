"""
Authentication dependencies for FastAPI routes.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.features.authenticate.infrastructure.adapters.jwt_service import jwt_service
from app.shared.domain.exceptions import UnauthorizedError


security = HTTPBearer()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    """
    FastAPI dependency that extracts the user_id from the JWT token.

    Usage:
        @router.get("/protected")
        async def protected_route(user_id: int = Depends(get_current_user_id)):
            ...
    """
    try:
        payload = jwt_service.decode_token(credentials.credentials)

        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user_id"
            )

        return user_id

    except UnauthorizedError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
