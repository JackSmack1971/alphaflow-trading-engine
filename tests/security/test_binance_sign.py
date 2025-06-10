from importlib import util
from pathlib import Path

spec = util.spec_from_file_location("binance", Path("shared/security/auth/binance.py").resolve())
mod = util.module_from_spec(spec)
spec.loader.exec_module(mod)

sign_params = mod.sign_params


def test_sign_params():
    params = {"a": "1", "b": "2"}
    result = sign_params(params, "secret")
    assert result.startswith("a=1&b=2&signature=")
