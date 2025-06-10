from __future__ import annotations

import asyncio
import time
from typing import Dict


class RateLimiter:
    """Simple per-key rate limiter."""

    def __init__(self, limit: int, window: int) -> None:
        self.limit = limit
        self.window = window
        self.calls: Dict[str, list[float]] = {}

    async def allow(self, key: str) -> bool:
        """Return True if request allowed for key."""
        now = time.monotonic()
        calls = [c for c in self.calls.get(key, []) if now - c < self.window]
        if len(calls) >= self.limit:
            return False
        calls.append(now)
        self.calls[key] = calls
        return True
