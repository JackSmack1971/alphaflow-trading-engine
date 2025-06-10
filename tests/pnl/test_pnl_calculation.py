import importlib.util
import sys
from pathlib import Path
from decimal import Decimal

import pytest

spec = importlib.util.spec_from_file_location(
    "pnl", Path("services/pnl/__init__.py").resolve()
)
mod = importlib.util.module_from_spec(spec)
sys.modules["pnl"] = mod
spec.loader.exec_module(mod)

PnLService = mod.PnLService
PricingError = mod.PricingError


def test_unrealized_and_realized() -> None:
    tracker = PnLService()
    tracker.on_fill("BTC", Decimal("10"), Decimal("100"))
    tracker.on_price("BTC", Decimal("110"))
    snap = tracker.snapshot()
    assert snap["realized"] == 0.0
    assert snap["unrealized"] == 100.0

    tracker.on_fill("BTC", Decimal("-5"), Decimal("115"))
    tracker.on_price("BTC", Decimal("120"))
    snap = tracker.snapshot()
    assert snap["realized"] == 75.0
    assert snap["unrealized"] == 100.0


def test_invalid_price() -> None:
    tracker = PnLService()
    tracker.on_fill("ETH", Decimal("1"), Decimal("100"))
    with pytest.raises(PricingError):
        tracker.on_price("ETH", Decimal("-1"))


def test_close_and_reverse() -> None:
    tracker = PnLService()
    tracker.on_fill("BTC", Decimal("5"), Decimal("100"))
    tracker.on_fill("BTC", Decimal("-10"), Decimal("90"))
    assert tracker.positions["BTC"].quantity == Decimal("-5")
    tracker.on_price("UNUSED", Decimal("10"))  # no position, should noop
    snap = tracker.snapshot()
    assert snap["total"] == -50.0


def test_close_position() -> None:
    tracker = PnLService()
    tracker.on_fill("BTC", Decimal("5"), Decimal("100"))
    tracker.on_fill("BTC", Decimal("-5"), Decimal("110"))
    assert tracker.positions["BTC"].quantity == 0
    assert tracker.positions["BTC"].avg_price == Decimal("0")
    snap = tracker.snapshot()
    assert snap["realized"] == 50.0
    assert snap["unrealized"] == 0.0



