"""Portfolio monitoring utilities."""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict


@dataclass
class Position:
    """Represents an open position."""

    quantity: Decimal = Decimal("0")
    avg_price: Decimal = Decimal("0")


@dataclass
class Portfolio:
    """Simple in-memory portfolio tracker."""

    positions: Dict[str, Position] = field(default_factory=dict)
    pnl: Decimal = Decimal("0")

    def update(self, symbol: str, quantity: Decimal, price: Decimal) -> None:
        pos = self.positions.setdefault(symbol, Position())
        new_qty = pos.quantity + quantity
        if new_qty == 0:
            pos.quantity = Decimal("0")
            pos.avg_price = Decimal("0")
        else:
            pos.avg_price = (
                (pos.avg_price * pos.quantity + price * quantity) / new_qty
            )
            pos.quantity = new_qty
        self.pnl += -price * quantity
