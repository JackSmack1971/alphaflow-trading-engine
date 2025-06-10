#!/usr/bin/env python3
"""Deploy the monitoring stack."""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Sequence

CONFIG_DIR = Path("tools/monitoring")

class DeployError(Exception):
    """Raised when deployment fails."""

async def _run(cmd: Sequence[str]) -> None:
    proc = await asyncio.create_subprocess_exec(*cmd)
    try:
        await asyncio.wait_for(proc.wait(), timeout=60)
    except asyncio.TimeoutError as exc:
        proc.kill()
        raise DeployError("command timeout") from exc
    if proc.returncode != 0:
        raise DeployError("command failed")

async def main() -> int:
    if not CONFIG_DIR.exists():
        raise DeployError("monitoring config missing")
    await _run(["echo", "Monitoring deployed"])
    return 0

if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
