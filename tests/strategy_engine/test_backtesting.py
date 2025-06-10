import pandas as pd
from decimal import Decimal

BACKTEST = "services.strategy-engine.backtesting.engine"
MA_CROSS = "services.strategy-engine.strategies.moving_average"

bt_mod = __import__(BACKTEST, fromlist=["Backtester"])
ma_mod = __import__(MA_CROSS, fromlist=["MovingAverageCrossover"])


def test_backtester_runs():
    data = pd.DataFrame({"close": [1, 2, 3, 2, 3, 4, 5, 4]})
    strat = ma_mod.MovingAverageCrossover("ma", Decimal("1"), 2, 3)
    bt = bt_mod.Backtester()
    result = bt.run(data, strat)
    assert isinstance(result.profit, Decimal)
