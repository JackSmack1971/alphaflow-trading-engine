import importlib.util
import sys
from pathlib import Path
from decimal import Decimal
import asyncio
import pytest


def load_risk_manager():
    spec = importlib.util.spec_from_file_location("risk_manager", Path("services/risk-manager/__init__.py").resolve())
    mod = importlib.util.module_from_spec(spec)
    sys.modules["risk_manager"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.asyncio
async def test_alert_queue_populated():
    risk_mod = load_risk_manager()
    q: asyncio.Queue[str] = asyncio.Queue()
    manager = risk_mod.RiskManager(alert_queue=q)
    order = risk_mod.Order("BTC", Decimal("11"), Decimal("1"), "BUY")
    with pytest.raises(risk_mod.exceptions_mod.RiskLimitBreached):
        await manager.validate_order(order)
    assert not q.empty()
    alert = await q.get()
    assert "limit" in alert
