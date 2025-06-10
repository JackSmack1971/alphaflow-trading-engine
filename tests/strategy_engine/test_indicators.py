import pandas as pd

MA = "services.strategy-engine.indicators.moving_average"
RSI = "services.strategy-engine.indicators.rsi"
BOLL = "services.strategy-engine.indicators.bollinger"

ma_mod = __import__(MA, fromlist=["moving_average"])
rsi_mod = __import__(RSI, fromlist=["rsi"])
boll_mod = __import__(BOLL, fromlist=["bollinger_bands"])


def test_moving_average():
    series = pd.Series([1, 2, 3, 4])
    ma = ma_mod.moving_average(series, 2)
    assert ma.iloc[-1] == 3.5


def test_rsi():
    series = pd.Series([1, 2, 3, 2, 1])
    values = rsi_mod.rsi(series, 2)
    assert len(values) == 5


def test_bollinger_bands():
    series = pd.Series([1, 2, 3, 4, 5])
    bands = boll_mod.bollinger_bands(series, 2)
    assert set(bands.columns) == {"upper", "lower"}
