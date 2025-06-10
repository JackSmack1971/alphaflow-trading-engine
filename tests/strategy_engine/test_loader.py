import importlib
from decimal import Decimal

import pandas as pd
import pytest

LOADER = "services.strategy-engine.strategies.loader"
MA_PATH = (
    "services.strategy-engine.strategies.moving_average.MovingAverageCrossover"
)
loader_mod = importlib.import_module(LOADER)


def test_load_strategy_allowed():
    strat = loader_mod.load_strategy(
        MA_PATH,
        "test",
        Decimal("1"),
        short_window="2",
        long_window="3",
    )
    assert strat.name == "test"


def test_invalid_path_rejected():
    with pytest.raises(loader_mod.LoaderError):
        loader_mod.load_strategy("os.system;rm", "bad", Decimal("1"))


def test_not_whitelisted():
    with pytest.raises(loader_mod.LoaderError):
        loader_mod.load_strategy("tests.strategy_engine.evil_strategy.EvilStrategy", "bad", Decimal("1"))


def test_sandbox_timeout(monkeypatch):
    path = "tests.strategy_engine.hang_strategy.HangStrategy"
    monkeypatch.setenv("STRATEGY_ALLOWLIST", f"{MA_PATH},{path}")
    importlib.reload(loader_mod)
    strat = loader_mod.load_strategy(path, "hang", Decimal("1"), timeout=0.1)
    with pytest.raises(loader_mod.StrategyError):
        strat.generate_signal(pd.DataFrame())
