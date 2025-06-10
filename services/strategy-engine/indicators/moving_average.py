"""Moving average indicator."""
from __future__ import annotations

from pandas import Series


def moving_average(series: Series, window: int) -> Series:
    """Calculate simple moving average."""
    return series.rolling(window=window).mean()
