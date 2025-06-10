"""Velocity limits."""
from __future__ import annotations

import time
from collections import deque
from typing import Deque, Dict, Optional

from .base import BaseLimit, Order
from ..monitors.portfolio import Portfolio


class VelocityLimit(BaseLimit):
    """Limit number of trades per time window."""

    def __init__(self, max_trades: int, window_sec: int) -> None:
        self.max_trades = max_trades
        self.window_sec = window_sec
        self.history: Deque[float] = deque()

    def check(
        self, order: Order, portfolio: Portfolio, prices: Dict[str, Decimal]
    ) -> Optional[str]:
        now = time.time()
        self.history.append(now)
        while self.history and now - self.history[0] > self.window_sec:
            self.history.popleft()
        if len(self.history) > self.max_trades:
            return "velocity limit"
        return None
