"""HashiCorp Vault integration."""

from __future__ import annotations

import asyncio
import os
from typing import Any, Dict, Tuple

import hvac

from shared.security.audit.logger import AuditLogger


class VaultError(Exception):
    """Raised when Vault operations fail."""


class VaultClient:
    """Simple Vault client wrapper with caching and audit logging."""

    def __init__(self, ttl: int = 300, logger: "AuditLogger | None" = None) -> None:
        addr = os.getenv("VAULT_ADDR")
        token = os.getenv("VAULT_TOKEN")
        if not addr or not token:
            raise VaultError("Vault configuration missing")
        self._client = hvac.Client(url=addr, token=token)
        self._ttl = ttl
        self._cache: Dict[Tuple[str, str], Tuple[str, float]] = {}
        self._logger = logger

    async def get_secret(self, path: str, key: str) -> str:
        """Fetch secret value with caching and retries."""
        cache_key = (path, key)
        now = asyncio.get_event_loop().time()
        if cache_key in self._cache:
            val, exp = self._cache[cache_key]
            if exp > now:
                return val
        for _ in range(3):
            try:
                val = await asyncio.to_thread(self._read_secret, path, key)
                self._cache[cache_key] = (val, now + self._ttl)
                if self._logger:
                    self._logger.log(f"read {path}:{key}")
                return val
            except hvac.exceptions.VaultError:
                await asyncio.sleep(1)
        raise VaultError(f"Unable to read secret {path}:{key}")

    def _read_secret(self, path: str, key: str) -> str:
        data = self._client.secrets.kv.read_secret_version(path=path)
        value = data["data"]["data"].get(key)
        if value is None:
            raise VaultError(f"Key {key} not found in {path}")
        return value
