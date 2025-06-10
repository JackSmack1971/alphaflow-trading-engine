"""Risk reporting placeholder."""
from __future__ import annotations

from typing import Dict
from decimal import Decimal

from ..monitors.portfolio import Portfolio


class Reporter:
    """Provides basic risk metrics."""

    async def snapshot(self, portfolio: Portfolio) -> Dict[str, float]:
        margin = sum(
            abs(p.quantity * p.avg_price) for p in portfolio.positions.values()
        ) * Decimal("0.1")
        return {
            "pnl": float(portfolio.pnl),
            "positions": len(portfolio.positions),
            "margin": float(margin),
        }
