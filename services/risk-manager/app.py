"""Risk management service."""
from __future__ import annotations

import os
from decimal import Decimal
from typing import List

from .circuit_breakers.drawdown import DrawdownCircuitBreaker
from .exceptions import CircuitBreakerTripped, RiskLimitBreached, ValidationError
from .limits.base import Order
from .limits.concentration import ConcentrationLimit
from .limits.daily_loss import DailyLossLimit
from .limits.drawdown import DrawdownLimit
from .limits.position import PositionLimit
from .limits.velocity import VelocityLimit
from .monitors.portfolio import Portfolio
from .reporting.reporter import Reporter


class RiskManager:
    """Main risk manager entry point."""

    def __init__(self) -> None:
        self.portfolio = Portfolio()
        self.limits: List = [
            PositionLimit(
                Decimal(os.getenv("POSITION_LIMIT_SYMBOL", "10")),
                Decimal(os.getenv("POSITION_LIMIT_TOTAL", "50")),
            ),
            DailyLossLimit(Decimal(os.getenv("DAILY_LOSS_LIMIT", "1000"))),
            ConcentrationLimit(Decimal(os.getenv("CONCENTRATION_LIMIT", "0.5"))),
            VelocityLimit(
                int(os.getenv("VELOCITY_LIMIT", "10")),
                int(os.getenv("VELOCITY_WINDOW", "60")),
            ),
            DrawdownLimit(Decimal(os.getenv("DRAWDOWN_LIMIT", "500"))),
        ]
        self.circuit_breakers = [
            DrawdownCircuitBreaker(
                Decimal(os.getenv("CIRCUIT_BREAKER_DRAWDOWN", "1000"))
            )
        ]
        self.reporter = Reporter()

    async def validate_order(self, order: Order) -> None:
        for cb in self.circuit_breakers:
            cb.check(self.portfolio)
        for limit in self.limits:
            reason = limit.check(order, self.portfolio)
            if reason:
                raise RiskLimitBreached(reason)

    async def on_fill(self, order: Order) -> None:
        self.portfolio.update(order.symbol, order.quantity, order.price)

    async def report(self) -> dict:
        return await self.reporter.snapshot(self.portfolio)
