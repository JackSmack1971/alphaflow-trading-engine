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
async def test_drawdown_circuit_breaker(monkeypatch) -> None:
    monkeypatch.setenv("CONCENTRATION_LIMIT", "1")
    monkeypatch.setenv("CIRCUIT_BREAKER_DRAWDOWN", "0")
    risk_mod = load_risk_manager()
    manager = risk_mod.RiskManager()
    await manager.on_fill(risk_mod.Order("BTC", Decimal("1"), Decimal("10"), "BUY"))
    with pytest.raises(risk_mod.exceptions_mod.CircuitBreakerTripped):
        await manager.validate_order(risk_mod.Order("BTC", Decimal("1"), Decimal("10"), "BUY"))
