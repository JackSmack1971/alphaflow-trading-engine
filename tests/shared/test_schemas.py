import json
from jsonschema import validate, ValidationError
from pathlib import Path

SCHEMAS = Path("shared/schemas")


def load_schema(name: str):
    with open(SCHEMAS / name) as f:
        return json.load(f)


def test_order_schema_valid():
    schema = load_schema("order.json")
    order = {
        "id": "1",
        "symbol": "BTC/USDT",
        "side": "BUY",
        "quantity": "0.1",
        "price": "50000",
        "timestamp": "2025-01-01T00:00:00Z",
    }
    validate(order, schema)


def test_order_schema_invalid_symbol():
    schema = load_schema("order.json")
    order = {
        "id": "1",
        "symbol": "INVALID",
        "side": "BUY",
        "quantity": "0.1",
        "price": "50000",
        "timestamp": "2025-01-01T00:00:00Z",
    }
    try:
        validate(order, schema)
    except ValidationError:
        assert True
    else:
        assert False
