from __future__ import annotations

"""JWT utilities for internal service authentication."""

import os
import time
from typing import Any, Dict

import jwt

SERVICE_JWT_SECRET = "SERVICE_JWT_SECRET"
SERVICE_NAME = "SERVICE_NAME"


class AuthError(Exception):
    """Raised on authentication failures."""


def _get_secret() -> str:
    secret = os.getenv(SERVICE_JWT_SECRET)
    if not secret:
        raise AuthError("missing jwt secret")
    return secret


def generate_token(service: str, ttl: int = 300) -> str:
    """Return a signed JWT."""
    payload = {"iss": service, "exp": int(time.time()) + ttl}
    return jwt.encode(payload, _get_secret(), algorithm="HS256")


def validate_token(token: str, issuer: str) -> Dict[str, Any]:
    """Validate token and return claims."""
    try:
        data = jwt.decode(token, _get_secret(), algorithms=["HS256"])
    except jwt.PyJWTError as exc:  # catch decode errors
        raise AuthError("invalid token") from exc
    if data.get("iss") != issuer:
        raise AuthError("invalid issuer")
    return data


class JWTTokenManager:
    """Manage JWT secrets with optional rotation via Vault."""

    def __init__(self, service: str, key_manager: Any | None = None) -> None:
        self.service = service
        self._key_manager = key_manager

    async def refresh(self) -> None:
        """Refresh secret using key manager if available."""
        if not self._key_manager:
            return
        new_secret = await self._key_manager.rotate(self.service, os.getenv("ENV", "dev"), "jwt_secret")
        os.environ[SERVICE_JWT_SECRET] = new_secret

    def token(self, ttl: int = 300) -> str:
        """Generate a token using current secret."""
        return generate_token(self.service, ttl)
