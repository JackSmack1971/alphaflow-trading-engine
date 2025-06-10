"""Bollinger Band Squeeze strategy."""
from __future__ import annotations

from decimal import Decimal
from typing import Optional

import pandas as pd

from ..indicators.bollinger import bollinger_bands
from ..signals.generator import create_signal
from ..signals.models import Signal
from .base import BaseStrategy, StrategyError


class BollingerSqueeze(BaseStrategy):
    """Breakout from narrow Bollinger Bands."""

    window: int
    threshold: float

    def __init__(self, name: str, position_size: Decimal, window: int = 20, threshold: float = 0.02) -> None:
        super().__init__(name=name, position_size=position_size)
        self.window = window
        self.threshold = threshold

    def generate_signal(self, data: pd.DataFrame) -> Optional[Signal]:
        """Signal on band squeeze breakout."""
        try:
            bands = bollinger_bands(data["close"], self.window)
        except Exception as exc:  # pragma: no cover
            raise StrategyError(str(exc)) from exc
        if bands.empty:
            return None
        width = (bands["upper"] - bands["lower"]) / bands["upper"]
        breakout_up = width.iloc[-1] > self.threshold and data["close"].iloc[-1] > bands["upper"].iloc[-1]
        breakout_down = width.iloc[-1] > self.threshold and data["close"].iloc[-1] < bands["lower"].iloc[-1]
        price = Decimal(str(data["close"].iloc[-1]))
        if breakout_up:
            return create_signal("BUY", price, self.position_size)
        if breakout_down:
            return create_signal("SELL", price, self.position_size)
        return None
