"""Real-time P&L tracking with mark-to-market pricing."""
from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List

import backoff

from .exceptions import PricingError


@dataclass
class Position:
    """Represents an open trading position."""

    quantity: Decimal = Decimal("0")
    avg_price: Decimal = Decimal("0")
    realized: Decimal = Decimal("0")
    last_price: Decimal = Decimal("0")

    def update(self, qty: Decimal, price: Decimal) -> None:
        same_side = self.quantity * qty >= 0
        if same_side:
            total_qty = self.quantity + qty
            if total_qty:
                self.avg_price = (
                    (self.avg_price * self.quantity) + (price * qty)
                ) / total_qty
            self.quantity = total_qty
        else:
            closed = min(abs(qty), abs(self.quantity))
            sign = Decimal("1") if self.quantity > 0 else Decimal("-1")
            self.realized += (price - self.avg_price) * closed * sign
            self.quantity += qty
            if self.quantity == 0:
                self.avg_price = Decimal("0")
            if abs(qty) > closed:
                self.avg_price = price
        self.last_price = price

    def mark(self, price: Decimal) -> None:
        if price <= 0:
            raise PricingError(f"invalid price {price}")
        self.last_price = price

    @property
    def unrealized(self) -> Decimal:
        return (self.last_price - self.avg_price) * self.quantity


class PnLService:
    """Tracks portfolio P&L in real time."""

    def __init__(self) -> None:
        self.positions: Dict[str, Position] = {}
        self.history: List[Dict[str, float]] = []

    def on_fill(self, symbol: str, qty: Decimal, price: Decimal) -> None:
        pos = self.positions.setdefault(symbol, Position())
        pos.update(qty, price)

    def on_price(self, symbol: str, price: Decimal) -> None:
        pos = self.positions.get(symbol)
        if not pos:
            return
        pos.mark(price)

    def snapshot(self) -> Dict[str, float]:
        realized = sum(p.realized for p in self.positions.values())
        unrealized = sum(p.unrealized for p in self.positions.values())
        snap = {
            "realized": float(realized),
            "unrealized": float(unrealized),
            "total": float(realized + unrealized),
        }
        self.history.append(snap)
        return snap

    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    async def listen_market_data(self, channel: str = "market") -> None:
        import redis.asyncio as aioredis

        url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        redis = aioredis.from_url(url)
        pubsub = redis.pubsub()
        await pubsub.subscribe(channel)
        async for msg in pubsub.listen():
            if msg.get("type") != "message":
                continue
            try:
                data = json.loads(msg["data"])
                symbol = data["symbol"]
                price = Decimal(str(data["price"]))
                self.on_price(symbol, price)
            except (KeyError, ValueError) as exc:
                raise PricingError("invalid pricing data") from exc

