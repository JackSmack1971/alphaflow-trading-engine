from importlib import util
from pathlib import Path

spec = util.spec_from_file_location("logging_utils", Path("shared/utils/logging_utils.py").resolve())
log_mod = util.module_from_spec(spec)
spec.loader.exec_module(log_mod)
get_logger = log_mod.get_logger


def test_get_logger_returns_logger():
    logger = get_logger("test")
    logger.info("hello")
    assert logger.name == "test"
