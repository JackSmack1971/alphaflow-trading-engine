"""Concentration limits."""
from __future__ import annotations

from decimal import Decimal
from typing import Dict, Optional

from .base import BaseLimit, Order
from ..monitors.portfolio import Portfolio


class ConcentrationLimit(BaseLimit):
    """Maximum percent allocation to a single asset."""

    def __init__(self, max_percent: Decimal) -> None:
        self.max_percent = max_percent

    def check(
        self, order: Order, portfolio: Portfolio, prices: Dict[str, Decimal]
    ) -> Optional[str]:
        total_value = sum(
            abs(p.quantity * prices.get(sym, p.avg_price))
            for sym, p in portfolio.positions.items()
        ) + abs(order.quantity * prices.get(order.symbol, order.price))
        if total_value == 0:
            return None
        existing = portfolio.positions.get(order.symbol)
        existing_value = (
            abs(existing.quantity * prices.get(order.symbol, existing.avg_price))
            if existing
            else Decimal("0")
        )
        sym_value = existing_value + abs(order.quantity * prices.get(order.symbol, order.price))
        if (sym_value / total_value) > self.max_percent:
            return "concentration limit"
        return None
