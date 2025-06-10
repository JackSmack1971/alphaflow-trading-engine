"""Simple backtesting engine."""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import List

import pandas as pd

from ..signals.models import Signal
from ..strategies.base import BaseStrategy


@dataclass
class Trade:
    """Executed trade record."""

    signal: Signal
    pnl: Decimal


@dataclass
class BacktestResult:
    """Aggregated metrics."""

    trades: List[Trade] = field(default_factory=list)
    profit: Decimal = Decimal("0")


class Backtester:
    """Run strategies on historical data."""

    def __init__(self, slippage: Decimal = Decimal("0"), commission: Decimal = Decimal("0")) -> None:
        self.slippage = slippage
        self.commission = commission

    def run(self, data: pd.DataFrame, strategy: BaseStrategy) -> BacktestResult:
        result = BacktestResult()
        for i in range(len(data)):
            df = data.iloc[: i + 1]
            signal = strategy.generate_signal(df)
            if signal:
                price = signal.price * (1 + self.slippage)
                cost = price * signal.quantity
                fee = cost * self.commission
                result.profit -= cost + fee if signal.action == "BUY" else -(cost - fee)
                result.trades.append(Trade(signal=signal, pnl=result.profit))
        return result
