"""Config loader with Vault integration and validation."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from jsonschema import validate, ValidationError

from .vault import VaultClient, VaultError
from .schema import CONFIG_SCHEMA


class ConfigError(Exception):
    """Configuration loading failure."""


@dataclass
class ConfigLoader:
    """Load and validate configuration."""

    env: str
    config_dir: Path = Path("config")
    vault_client: Optional[VaultClient] = None

    async def _read_file(self, path: Path) -> Dict[str, Any]:
        data = await asyncio.to_thread(path.read_text)
        return yaml.safe_load(data)

    async def _load_secrets(self) -> Dict[str, Any]:
        if not self.vault_client:
            return {}
        secrets = {}
        for key in ("api_key", "db_password"):
            secret = await self.vault_client.get_secret(f"alphaflow/{self.env}", key)
            secrets[key] = secret
        return secrets

    async def load(self) -> Dict[str, Any]:
        path = self.config_dir / f"{self.env}.yaml"
        if not path.exists():
            raise ConfigError(f"Config file {path} missing")
        cfg = await self._read_file(path)
        try:
            validate(cfg, CONFIG_SCHEMA)
        except ValidationError as exc:
            raise ConfigError(str(exc)) from exc
        secrets = await self._load_secrets()
        cfg.update(secrets)
        if "api_key" not in cfg or "db_password" not in cfg:
            raise ConfigError("Missing critical configuration")
        return cfg
