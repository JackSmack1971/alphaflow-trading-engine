"""Position size limits."""
from __future__ import annotations

from decimal import Decimal
from typing import Dict, Optional

from .base import BaseLimit, Order
from ..monitors.portfolio import Portfolio


class PositionLimit(BaseLimit):
    """Enforces per-symbol and total position size limits."""

    def __init__(self, symbol_limit: Decimal, total_limit: Decimal) -> None:
        self.symbol_limit = symbol_limit
        self.total_limit = total_limit

    def check(
        self, order: Order, portfolio: Portfolio, prices: Dict[str, Decimal]
    ) -> Optional[str]:
        sym_qty = portfolio.positions.get(order.symbol, None)
        current = sym_qty.quantity if sym_qty else Decimal("0")
        if abs(current + order.quantity) > self.symbol_limit:
            return "symbol position limit"
        total = sum(abs(p.quantity) for p in portfolio.positions.values())
        if total + abs(order.quantity) > self.total_limit:
            return "total position limit"
        return None
