"""Drawdown circuit breaker."""
from __future__ import annotations

from decimal import Decimal

from ..exceptions import CircuitBreakerTripped
from ..monitors.portfolio import Portfolio


class DrawdownCircuitBreaker:
    """Halts trading if drawdown exceeds threshold."""

    def __init__(self, threshold: Decimal) -> None:
        self.threshold = threshold
        self.high_watermark = Decimal("0")
        self.tripped = False

    def check(self, portfolio: Portfolio) -> None:
        if self.tripped:
            raise CircuitBreakerTripped("circuit breaker active")
        pnl = portfolio.pnl
        if pnl > self.high_watermark:
            self.high_watermark = pnl
        drawdown = self.high_watermark - pnl
        if drawdown > self.threshold:
            self.tripped = True
            raise CircuitBreakerTripped("drawdown threshold exceeded")
