from __future__ import annotations

import asyncio
from typing import Optional

from shared.config.vault import VaultClient, VaultError


class RotationError(Exception):
    """Raised when API key rotation fails."""


class APIKeyManager:
    """Manage API keys stored in Vault."""

    def __init__(self, client: Optional[VaultClient] = None) -> None:
        self.client = client or VaultClient()

    async def rotate(self, service: str, env: str, key_field: str = "api_key") -> str:
        """Rotate and return new API key."""
        if not service or not env:
            raise RotationError("service and env required")
        for _ in range(3):
            try:
                path = f"{service}/{env}"
                new_key = await self.client.get_secret(path, key_field)
                return new_key
            except VaultError:
                await asyncio.sleep(1)
        raise RotationError(f"failed to rotate key for {service} {env}")
