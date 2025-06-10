from importlib import util
from pathlib import Path
import asyncio
import pytest

spec_mgr = util.spec_from_file_location("manager", Path("shared/security/vault/key_manager.py").resolve())
manager_mod = util.module_from_spec(spec_mgr)
spec_mgr.loader.exec_module(manager_mod)

spec_vault = util.spec_from_file_location("vault", Path("shared/config/vault.py").resolve())
vault_mod = util.module_from_spec(spec_vault)
spec_vault.loader.exec_module(vault_mod)

class DummyVault(vault_mod.VaultClient):
    def __init__(self) -> None:
        pass

    async def get_secret(self, path: str, key: str) -> str:  # type: ignore[override]
        return "rotated"

@pytest.mark.asyncio
async def test_rotate_success():
    mgr = manager_mod.APIKeyManager(client=DummyVault())
    key = await mgr.rotate("svc", "prod")
    assert key == "rotated"

@pytest.mark.asyncio
async def test_rotate_invalid():
    mgr = manager_mod.APIKeyManager(client=DummyVault())
    with pytest.raises(manager_mod.RotationError):
        await mgr.rotate("", "")
