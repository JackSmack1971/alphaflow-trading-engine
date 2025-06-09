#!/usr/bin/env python3
"""Validate all environment configurations."""
from __future__ import annotations

import asyncio

from shared.config import get_config_loader


class DummyVault:
    async def get_secret(self, path: str, key: str) -> str:  # noqa: D401
        """Return placeholder secret."""
        return "placeholder"


async def main() -> int:
    for env in ("local", "staging", "production"):
        loader = get_config_loader()
        loader.env = env
        loader.vault_client = DummyVault()
        try:
            await loader.load()
            print(f"{env} configuration valid")
        except Exception as exc:  # noqa: BLE001
            print(f"{env} configuration invalid: {exc}")
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
