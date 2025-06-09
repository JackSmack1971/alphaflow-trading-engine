from decimal import Decimal
from importlib import util
from pathlib import Path

spec = util.spec_from_file_location(
    "decimal_utils", Path("shared/utils/decimal_utils.py").resolve()
)
dec_mod = util.module_from_spec(spec)
spec.loader.exec_module(dec_mod)

spec_cfg = util.spec_from_file_location("config", Path("shared/utils/config.py").resolve())
cfg_mod = util.module_from_spec(spec_cfg)
spec_cfg.loader.exec_module(cfg_mod)

to_decimal = dec_mod.to_decimal
load_config = cfg_mod.load_config


def test_to_decimal():
    assert to_decimal("1.23") == Decimal("1.23")


def test_load_config(monkeypatch):
    monkeypatch.setenv("REDIS_URL", "redis://test")
    monkeypatch.setenv("DB_URL", "postgresql://test/db")
    cfg = load_config()
    assert cfg.redis_url == "redis://test"
    assert cfg.db_url == "postgresql://test/db"
