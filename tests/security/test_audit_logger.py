from importlib import util
from pathlib import Path

spec = util.spec_from_file_location("audit", Path("shared/security/audit/logger.py").resolve())
audit_mod = util.module_from_spec(spec)
spec.loader.exec_module(audit_mod)
AuditLogger = audit_mod.AuditLogger


def test_audit_logger(tmp_path):
    path = tmp_path / "audit.log"
    logger = AuditLogger(path)
    logger.log("event")
    assert path.exists() and path.read_text()
