from __future__ import annotations

"""JWT utilities for internal service authentication."""

import os
import time
import asyncio
from typing import Any, Dict

import jwt

from shared.security.vault.key_manager import APIKeyManager

SERVICE_JWT_SECRET = "SERVICE_JWT_SECRET"
SERVICE_NAME = "SERVICE_NAME"


class AuthError(Exception):
    """Raised on authentication failures."""


_key_manager: "APIKeyManager | None" = None
_secret_cache = ""


def set_key_manager(manager: "APIKeyManager") -> None:
    """Override key manager, primarily for tests."""
    global _key_manager
    _key_manager = manager


def _get_secret() -> str:
    global _secret_cache
    if _secret_cache:
        return _secret_cache
    service = os.getenv(SERVICE_NAME, "unknown")
    env = os.getenv("ENV", "dev")
    manager = _key_manager or APIKeyManager()
    try:
        _secret_cache = asyncio.run(manager.rotate(service, env, "jwt_secret"))
        return _secret_cache
    except Exception as exc:
        raise AuthError("missing jwt secret") from exc


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
        self._key_manager = key_manager or APIKeyManager()
        self._secret = ""

    async def refresh(self) -> None:
        """Refresh secret using key manager if available."""
        new_secret = await self._key_manager.rotate(
            self.service, os.getenv("ENV", "dev"), "jwt_secret"
        )
        self._secret = new_secret
        global _secret_cache
        _secret_cache = new_secret

    def token(self, ttl: int = 300) -> str:
        """Generate a token using current secret."""
        if not self._secret:
            asyncio.run(self.refresh())
        return jwt.encode(
            {"iss": self.service, "exp": int(time.time()) + ttl},
            self._secret,
            algorithm="HS256",
        )
