"""Risk management service."""
from __future__ import annotations

import os
import asyncio
from decimal import Decimal
from typing import Dict, List, Optional

from .circuit_breakers.drawdown import DrawdownCircuitBreaker
from .exceptions import CircuitBreakerTripped, RiskLimitBreached, ValidationError
from .limits.base import Order
from .limits.concentration import ConcentrationLimit
from .limits.daily_loss import DailyLossLimit
from .limits.drawdown import DrawdownLimit
from .limits.position import PositionLimit
from .limits.velocity import VelocityLimit
from .monitors.portfolio import Portfolio, Position
from .monitors.realtime import RealTimeMonitor
from services.pnl import PnLService
from .reporting.reporter import Reporter


class RiskManager:
    """Main risk manager entry point."""

    def __init__(
        self,
        pnl_service: Optional[PnLService] = None,
        alert_queue: Optional[asyncio.Queue[str]] = None,
    ) -> None:
        self.portfolio = Portfolio()
        self.pnl_service = pnl_service or PnLService()
        self.alerts = RealTimeMonitor(alert_queue or asyncio.Queue())
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
            reason = limit.check(order, self.portfolio, self.pnl_service.prices)
            if reason:
                await self.alerts.alert(reason)
                raise RiskLimitBreached(reason)

    async def on_fill(self, order: Order) -> None:
        self.portfolio.update(order.symbol, order.quantity, order.price)
        self.pnl_service.on_fill(order.symbol, order.quantity, order.price)

    async def report(self) -> dict:
        return await self.reporter.snapshot(self.portfolio)

    def margin(self) -> Decimal:
        """Calculate portfolio margin requirement."""
        return sum(
            abs(p.quantity * p.last_price)
            for p in self.pnl_service.positions.values()
        ) * Decimal("0.1")

    def stress_test(self, shocks: Dict[str, Decimal]) -> Decimal:
        """Apply price shocks and return projected PnL."""
        pnl = Decimal("0")
        for sym, pos in self.pnl_service.positions.items():
            shock = shocks.get(sym, Decimal("0"))
            pnl += pos.quantity * (pos.last_price + shock - pos.last_price)
        return pnl

    def rebalance(self, targets: Dict[str, Decimal]) -> List[Order]:
        """Generate orders to match target quantities."""
        orders: List[Order] = []
        for sym, target in targets.items():
            current = self.portfolio.positions.get(sym, Position()).quantity
            diff = target - current
            if diff:
                price = self.pnl_service.prices.get(sym, Decimal("0"))
                orders.append(Order(symbol=sym, quantity=diff, price=price, side="BUY" if diff > 0 else "SELL"))
        return orders
