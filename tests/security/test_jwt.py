from fastapi import FastAPI
from fastapi.testclient import TestClient
import os

from shared.security.auth.jwt import set_key_manager

from shared.security.auth import (
    generate_token,
    validate_token,
    AuthError,
    JWTTokenManager,
)
from shared.security.auth.fastapi import AuthMiddleware


def test_token_generation_and_validation():
    class KM:
        async def rotate(
            self, service: str, env: str, key_field: str = "jwt_secret"
        ) -> str:
            return "secret"

    set_key_manager(KM())
    token = generate_token("svc")
    claims = validate_token(token, "svc")
    assert claims["iss"] == "svc"


def test_fastapi_auth_middleware():
    class KM:
        async def rotate(
            self, service: str, env: str, key_field: str = "jwt_secret"
        ) -> str:
            return "secret"

    set_key_manager(KM())
    app = FastAPI()
    app.state.service_name = "svc"
    app.add_middleware(AuthMiddleware)

    @app.get("/ping")
    async def ping():
        return {"status": "ok"}

    client = TestClient(app)
    resp = client.get("/ping")
    assert resp.status_code == 401
    token = generate_token("svc")
    resp = client.get("/ping", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


class DummyKeyManager:
    async def rotate(
        self, service: str, env: str, key_field: str = "jwt_secret"
    ) -> str:
        return "newsecret"


def test_token_manager_refresh():
    mgr = DummyKeyManager()
    tm = JWTTokenManager("svc", mgr)
    import asyncio

    asyncio.run(tm.refresh())
    assert tm._secret == "newsecret"
