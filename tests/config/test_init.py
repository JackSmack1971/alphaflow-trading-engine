from importlib import import_module
import asyncio
from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

config_mod = import_module("shared.config")


@pytest.mark.asyncio
async def test_load_config(tmp_path, monkeypatch):
    cfg_file = tmp_path / "local.yaml"
    cfg_dir = tmp_path
    cfg_file.write_text("app:\n  name: t\n  log_level: INFO\ndatabase:\n  host: h\n  port: 1\n  name: d\nredis:\n  host: r\n  port: 2\n")
    monkeypatch.setenv("ALPHAFLOW_ENV", "local")
    monkeypatch.setenv("CONFIG_DIR", str(cfg_dir))

    class DummyVault:
        async def get_secret(self, path: str, key: str) -> str:
            return "v"

    loader = config_mod.get_config_loader()
    loader.vault_client = DummyVault()
    cfg = await loader.load()
    assert cfg["api_key"] == "v"
