"""Real-time risk alert monitor."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass


@dataclass
class RealTimeMonitor:
    """Broadcasts risk alerts through an asyncio queue."""

    queue: asyncio.Queue[str]

    async def alert(self, message: str) -> None:
        """Send alert asynchronously."""
        await self.queue.put(message)
