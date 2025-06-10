"""Risk reporting placeholder."""
from __future__ import annotations

from typing import Dict

from ..monitors.portfolio import Portfolio


class Reporter:
    """Provides basic risk metrics."""

    async def snapshot(self, portfolio: Portfolio) -> Dict[str, float]:
        return {
            "pnl": float(portfolio.pnl),
            "positions": len(portfolio.positions),
        }
