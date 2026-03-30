"""
JWT service implementation for ROGER - Valeria API
"""

from datetime import datetime, timedelta
from typing import Dict
from jose import JWTError, jwt

from app.features.authenticate.domain.auth_port import IJWTService
from app.config.settings import settings
from app.shared.domain.exceptions import UnauthorizedError


class JWTService(IJWTService):
    """JWT service for creating and verifying tokens."""
    
    def __init__(self):
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_expire = settings.access_token_expire_minutes
        self.refresh_token_expire = settings.refresh_token_expire_days
    
    def create_access_token(self, data: Dict) -> str:
        """Create an access token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire)
        to_encode.update({"exp": expire, "type": "access"})
        
        encoded_jwt = jwt.encode(
            to_encode,
            self.secret_key,
            algorithm=self.algorithm
        )
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict) -> str:
        """Create a refresh token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire)
        to_encode.update({"exp": expire, "type": "refresh"})
        
        encoded_jwt = jwt.encode(
            to_encode,
            self.secret_key,
            algorithm=self.algorithm
        )
        return encoded_jwt
    
    def decode_token(self, token: str) -> Dict:
        """Decode and verify a token."""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
        except JWTError as e:
            raise UnauthorizedError(f"Invalid token: {str(e)}")

    def create_email_verification_token(self, email: str, code_hash: str) -> str:
        """Create a short-lived email verification token (10 min)."""
        expire = datetime.utcnow() + timedelta(minutes=10)
        payload = {
            "sub": email,
            "code_hash": code_hash,
            "exp": expire,
            "type": "email_verify",
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def decode_email_verification_token(self, token: str) -> Dict:
        """Decode an email verification token and validate its type."""
        payload = self.decode_token(token)
        if payload.get("type") != "email_verify":
            raise UnauthorizedError("Invalid token type")
        return payload

    def create_reset_token(self, user_id: int, email: str) -> str:
        """Create a short-lived password reset token (15 min)."""
        expire = datetime.utcnow() + timedelta(
            minutes=settings.reset_token_expire_minutes
        )
        payload = {
            "sub": email,
            "user_id": user_id,
            "exp": expire,
            "type": "reset",
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def decode_reset_token(self, token: str) -> Dict:
        """Decode a reset token and validate its type."""
        payload = self.decode_token(token)
        if payload.get("type") != "reset":
            raise UnauthorizedError("Invalid token type")
        return payload


# Global instance
jwt_service = JWTService()
