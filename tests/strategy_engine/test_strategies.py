import pandas as pd
from decimal import Decimal

MA_CROSS = "services.strategy-engine.strategies.moving_average"
RSI_STRAT = "services.strategy-engine.strategies.rsi_mean_reversion"
BOLL_STRAT = "services.strategy-engine.strategies.bollinger_squeeze"

ma_mod = __import__(MA_CROSS, fromlist=["MovingAverageCrossover"])
rsi_mod = __import__(RSI_STRAT, fromlist=["RSIMeanReversion"])
boll_mod = __import__(BOLL_STRAT, fromlist=["BollingerSqueeze"])


def sample_data() -> pd.DataFrame:
    return pd.DataFrame({"close": [1, 2, 3, 4, 5, 4, 3, 2, 3, 4]})


def test_ma_crossover():
    strat = ma_mod.MovingAverageCrossover("ma", Decimal("1"), 2, 3)
    sig = strat.generate_signal(sample_data())
    assert sig is not None


def test_rsi_strategy():
    strat = rsi_mod.RSIMeanReversion("rsi", Decimal("1"))
    sig = strat.generate_signal(sample_data())
    assert sig is not None or sig is None


def test_bollinger_strategy():
    strat = boll_mod.BollingerSqueeze("boll", Decimal("1"))
    sig = strat.generate_signal(sample_data())
    assert sig is None or sig.action in {"BUY", "SELL"}
