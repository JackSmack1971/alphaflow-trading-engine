import importlib.util
import sys
from pathlib import Path
from decimal import Decimal
import pytest


def load_risk_manager():
    spec = importlib.util.spec_from_file_location("risk_manager", Path("services/risk-manager/__init__.py").resolve())
    mod = importlib.util.module_from_spec(spec)
    sys.modules["risk_manager"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.asyncio
async def test_position_limit() -> None:
    risk_mod = load_risk_manager()
    manager = risk_mod.RiskManager()
    order = risk_mod.Order(symbol="BTCUSDT", quantity=Decimal("11"), price=Decimal("1"), side="BUY")
    with pytest.raises(risk_mod.exceptions_mod.RiskLimitBreached):
        await manager.validate_order(order)


@pytest.mark.asyncio
async def test_concentration_limit(monkeypatch) -> None:
    monkeypatch.setenv("CONCENTRATION_LIMIT", "0.1")
    risk_mod = load_risk_manager()
    manager = risk_mod.RiskManager()
    order = risk_mod.Order(symbol="ETHUSDT", quantity=Decimal("5"), price=Decimal("200"), side="BUY")
    await manager.on_fill(order)
    big_order = risk_mod.Order(symbol="ETHUSDT", quantity=Decimal("5"), price=Decimal("200"), side="BUY")
    with pytest.raises(risk_mod.exceptions_mod.RiskLimitBreached):
        await manager.validate_order(big_order)
