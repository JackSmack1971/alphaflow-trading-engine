"""Bollinger Bands indicator."""
from __future__ import annotations

import pandas as pd


def bollinger_bands(series: pd.Series, window: int, num_std: float = 2.0) -> pd.DataFrame:
    """Calculate Bollinger Bands."""
    sma = series.rolling(window).mean()
    std = series.rolling(window).std()
    upper = sma + num_std * std
    lower = sma - num_std * std
    return pd.DataFrame({"upper": upper, "lower": lower})
