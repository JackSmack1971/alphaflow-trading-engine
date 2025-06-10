from decimal import Decimal

LOADER = "services.strategy-engine.strategies.loader"
MA = "services.strategy-engine.strategies.moving_average"

loader_mod = __import__(LOADER, fromlist=["load_strategy"])


def test_load_strategy():
    strat = loader_mod.load_strategy(f"{MA}.MovingAverageCrossover", "test", Decimal("1"), 2, 3)
    assert strat.name == "test"
