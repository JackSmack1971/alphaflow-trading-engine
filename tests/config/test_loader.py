from importlib import import_module
from pathlib import Path
import asyncio
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

loader_mod = import_module("shared.config.loader")
vault_mod = import_module("shared.config.vault")


class DummyVault(vault_mod.VaultClient):
    def __init__(self) -> None:
        pass

    async def get_secret(self, path: str, key: str) -> str:  # type: ignore[override]
        secrets = {"api_key": "test", "db_password": "pass"}
        return secrets[key]


def test_load_local_config(tmp_path):
    cfg_file = tmp_path / "config/local.yaml"
    cfg_file.parent.mkdir()
    cfg_file.write_text(
        "app:\n  name: t\n  log_level: INFO\ndatabase:\n  host: h\n  port: 1\n  name: d\nredis:\n  host: r\n  port: 2\n"
    )
    loader = loader_mod.ConfigLoader(env="local", config_dir=cfg_file.parent, vault_client=DummyVault())
    cfg = asyncio.run(loader.load())
    assert cfg["app"]["name"] == "t"
    assert cfg["api_key"] == "test"


def test_missing_config(tmp_path):
    loader = loader_mod.ConfigLoader(env="missing", config_dir=tmp_path)
    with pytest.raises(loader_mod.ConfigError):
        asyncio.run(loader.load())
