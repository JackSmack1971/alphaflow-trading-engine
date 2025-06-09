from importlib import import_module
from pathlib import Path
import asyncio
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

loader_mod = import_module("shared.config.loader")
reloader_mod = import_module("shared.config.reloader")


class DummyLoader(loader_mod.ConfigLoader):
    async def load(self) -> dict:  # type: ignore[override]
        return {"value": 1}


@pytest.mark.asyncio
async def test_reloader_triggers_callback(tmp_path):
    loader = DummyLoader(env="local", config_dir=tmp_path)
    result = {}

    def cb(cfg):
        result.update(cfg)

    reloader = reloader_mod.ConfigReloader(loader, cb)
    await reloader._reload()
    assert result == {"value": 1}
