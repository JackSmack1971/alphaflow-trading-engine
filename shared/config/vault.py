"""HashiCorp Vault integration."""
from __future__ import annotations

import asyncio
import os
from typing import Any

import hvac


class VaultError(Exception):
    """Raised when Vault operations fail."""


class VaultClient:
    """Simple Vault client wrapper."""

    def __init__(self) -> None:
        addr = os.getenv("VAULT_ADDR")
        token = os.getenv("VAULT_TOKEN")
        if not addr or not token:
            raise VaultError("Vault configuration missing")
        self._client = hvac.Client(url=addr, token=token)

    async def get_secret(self, path: str, key: str) -> str:
        """Fetch secret value asynchronously with retries."""
        for _ in range(3):
            try:
                return await asyncio.to_thread(self._read_secret, path, key)
            except hvac.exceptions.VaultError:
                await asyncio.sleep(1)
        raise VaultError(f"Unable to read secret {path}:{key}")

    def _read_secret(self, path: str, key: str) -> str:
        data = self._client.secrets.kv.read_secret_version(path=path)
        value = data["data"]["data"].get(key)
        if value is None:
            raise VaultError(f"Key {key} not found in {path}")
        return value
