"""Moving Average Crossover strategy."""
from __future__ import annotations

from decimal import Decimal
from typing import Optional

import pandas as pd

from ..indicators.moving_average import moving_average
from ..signals.generator import create_signal
from ..signals.models import Signal
from .base import BaseStrategy, StrategyError


class MovingAverageCrossover(BaseStrategy):
    """Simple MA crossover strategy."""

    short_window: int
    long_window: int

    def __init__(self, name: str, position_size: Decimal, short_window: int, long_window: int) -> None:
        super().__init__(name=name, position_size=position_size)
        self.short_window = short_window
        self.long_window = long_window

    def generate_signal(self, data: pd.DataFrame) -> Optional[Signal]:
        """Generate signal based on MA crossover."""
        try:
            ma_short = moving_average(data["close"], self.short_window)
            ma_long = moving_average(data["close"], self.long_window)
        except Exception as exc:  # pragma: no cover - panda errors
            raise StrategyError(str(exc)) from exc
        if len(ma_short) < 2 or len(ma_long) < 2:
            return None
        cross_up = ma_short.iloc[-2] < ma_long.iloc[-2] and ma_short.iloc[-1] > ma_long.iloc[-1]
        cross_down = ma_short.iloc[-2] > ma_long.iloc[-2] and ma_short.iloc[-1] < ma_long.iloc[-1]
        price = Decimal(str(data["close"].iloc[-1]))
        if cross_up:
            return create_signal("BUY", price, self.position_size)
        if cross_down:
            return create_signal("SELL", price, self.position_size)
        return None
