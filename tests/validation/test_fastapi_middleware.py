from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from shared.validation.fastapi import ValidationMiddleware

app = FastAPI()
app.add_middleware(ValidationMiddleware, schemas={"/item": "strategy_request"})

@app.post("/item")
async def item(request: Request):
    return request.scope.get("state", {}).get("validated", {})

client = TestClient(app)

def test_valid_request():
    resp = client.post("/item", json={"path": "a.b", "position_size": "1"})
    assert resp.status_code == 200


def test_invalid_payload():
    resp = client.post("/item", json={"path": "a.b"})
    assert resp.status_code == 400


def test_request_too_large():
    big_param = "x" * (1024 * 1024)
    resp = client.post("/item", json={"path": "a.b", "position_size": "1", "params": {"b": big_param}})
    assert resp.status_code == 413


def test_content_type():
    resp = client.post("/item", data="{}", headers={"Content-Type": "text/plain"})
    assert resp.status_code == 415
