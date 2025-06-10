#!/usr/bin/env python3
"""Validate alert rules."""
from __future__ import annotations

import asyncio
from pathlib import Path
import yaml

ALERTS_FILE = Path("tools/monitoring/alerts/alerts.yaml")

class AlertError(Exception):
    """Raised when alert rules are invalid."""

async def main() -> int:
    if not ALERTS_FILE.exists():
        raise AlertError("alerts file missing")
    data = yaml.safe_load(await asyncio.to_thread(ALERTS_FILE.read_text))
    if not isinstance(data, list) or not data:
        raise AlertError("no alerts defined")
    return 0

if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
