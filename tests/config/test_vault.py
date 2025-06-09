from importlib import util
from pathlib import Path
import asyncio
import pytest

spec = util.spec_from_file_location(
    "vault", Path("shared/config/vault.py").resolve()
)
vault_mod = util.module_from_spec(spec)
spec.loader.exec_module(vault_mod)


class FakeClient:
    def __init__(self) -> None:
        self.calls = []

    class secrets:
        class kv:
            @staticmethod
            def read_secret_version(path: str):
                return {"data": {"data": {"api_key": "k"}}}


class DummyVault(vault_mod.VaultClient):
    def __init__(self) -> None:
        self._client = FakeClient()


@pytest.mark.asyncio
async def test_get_secret():
    client = DummyVault()
    val = await client.get_secret("p", "api_key")
    assert val == "k"


@pytest.mark.asyncio
async def test_missing_key_raises():
    client = DummyVault()
    with pytest.raises(vault_mod.VaultError):
        await client.get_secret("p", "missing")
