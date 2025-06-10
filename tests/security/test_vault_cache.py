from importlib import util
from pathlib import Path

audit_spec = util.spec_from_file_location(
    "audit", Path("shared/security/audit/logger.py").resolve()
)
audit_mod = util.module_from_spec(audit_spec)
audit_spec.loader.exec_module(audit_mod)

vault_spec = util.spec_from_file_location(
    "vault", Path("shared/config/vault.py").resolve()
)
vault_mod = util.module_from_spec(vault_spec)
vault_spec.loader.exec_module(vault_mod)


CALLS = 0


class DummyClient:
    def __init__(self) -> None:
        pass

    class secrets:
        class kv:
            @staticmethod
            def read_secret_version(path: str):
                global CALLS
                CALLS += 1
                return {"data": {"data": {"k": "v"}}}


class DummyVault(vault_mod.VaultClient):
    def __init__(self, ttl: int = 1, logger=None) -> None:
        self._client = DummyClient()
        self._ttl = ttl
        self._cache = {}
        self._logger = logger


import pytest


@pytest.mark.asyncio
async def test_cache_and_audit(tmp_path):
    log = tmp_path / "audit.log"
    logger = audit_mod.AuditLogger(log)
    client = DummyVault(logger=logger, ttl=60)
    val1 = await client.get_secret("p", "k")
    val2 = await client.get_secret("p", "k")
    assert val1 == val2 == "v"
    assert CALLS == 1
    assert log.exists() and "read p:k" in log.read_text()
