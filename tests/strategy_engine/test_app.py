from fastapi.testclient import TestClient
from decimal import Decimal

APP = "services.strategy-engine.app"
app_mod = __import__(APP, fromlist=["app", "manager"])

client = TestClient(app_mod.app)


def test_add_and_list_strategy():
    payload = {
        "path": "services.strategy-engine.strategies.moving_average.MovingAverageCrossover",
        "params": {"short_window": "2", "long_window": "3"},
        "position_size": "1",
    }
    resp = client.post("/strategies", json=payload)
    assert resp.status_code == 200
    resp2 = client.get("/strategies")
    assert resp2.status_code == 200
    assert payload["path"] in resp2.json()
