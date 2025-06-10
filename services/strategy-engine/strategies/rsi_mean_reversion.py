"""RSI mean reversion strategy."""
from __future__ import annotations

from decimal import Decimal
from typing import Optional

import pandas as pd

from ..indicators.rsi import rsi
from ..signals.generator import create_signal
from ..signals.models import Signal
from .base import BaseStrategy, StrategyError


class RSIMeanReversion(BaseStrategy):
    """Buy when RSI below threshold, sell when above."""

    window: int
    lower: float
    upper: float

    def __init__(self, name: str, position_size: Decimal, window: int = 14, lower: float = 30, upper: float = 70) -> None:
        super().__init__(name=name, position_size=position_size)
        self.window = window
        self.lower = lower
        self.upper = upper

    def generate_signal(self, data: pd.DataFrame) -> Optional[Signal]:
        """Generate signals based on RSI levels."""
        try:
            rsi_vals = rsi(data["close"], self.window)
        except Exception as exc:  # pragma: no cover
            raise StrategyError(str(exc)) from exc
        if rsi_vals.empty:
            return None
        current_rsi = rsi_vals.iloc[-1]
        price = Decimal(str(data["close"].iloc[-1]))
        if current_rsi < self.lower:
            return create_signal("BUY", price, self.position_size)
        if current_rsi > self.upper:
            return create_signal("SELL", price, self.position_size)
        return None
