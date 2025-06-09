"""Configuration utilities."""
from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Any, Dict

from .loader import ConfigLoader, ConfigError
from .reloader import ConfigReloader

__all__ = [
    "ConfigLoader",
    "ConfigError",
    "ConfigReloader",
    "get_config_loader",
    "load_config",
]


def get_config_loader() -> ConfigLoader:
    """Return loader based on ALPHAFLOW_ENV."""
    env = os.getenv("ALPHAFLOW_ENV", "local")
    config_dir = Path(os.getenv("CONFIG_DIR", "config"))
    return ConfigLoader(env=env, config_dir=config_dir)


async def load_config() -> Dict[str, Any]:
    """Convenience to load config asynchronously."""
    loader = get_config_loader()
    return await loader.load()
