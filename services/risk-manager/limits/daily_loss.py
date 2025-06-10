"""Daily loss limits."""
from __future__ import annotations

from decimal import Decimal
from typing import Dict, Optional

from .base import BaseLimit, Order
from ..monitors.portfolio import Portfolio


class DailyLossLimit(BaseLimit):
    """Stop trading after max daily loss."""

    def __init__(self, max_loss: Decimal) -> None:
        self.max_loss = max_loss

    def check(
        self, order: Order, portfolio: Portfolio, prices: Dict[str, Decimal]
    ) -> Optional[str]:
        if portfolio.pnl < -self.max_loss:
            return "daily loss limit"
        return None
