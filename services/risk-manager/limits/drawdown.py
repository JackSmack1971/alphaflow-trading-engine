"""Drawdown limits."""
from __future__ import annotations

from decimal import Decimal
from typing import Optional

from .base import BaseLimit, Order
from ..monitors.portfolio import Portfolio


class DrawdownLimit(BaseLimit):
    """Protect against large drawdowns."""

    def __init__(self, max_drawdown: Decimal) -> None:
        self.max_drawdown = max_drawdown
        self.high_watermark = Decimal("0")

    def check(self, order: Order, portfolio: Portfolio) -> Optional[str]:
        pnl = portfolio.pnl
        if pnl > self.high_watermark:
            self.high_watermark = pnl
        drawdown = self.high_watermark - pnl
        if drawdown > self.max_drawdown:
            return "drawdown limit"
        return None
