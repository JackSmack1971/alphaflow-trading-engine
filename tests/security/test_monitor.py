from importlib import util
from pathlib import Path

spec = util.spec_from_file_location("events", Path("shared/security/monitoring/events.py").resolve())
mod = util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_monitor_alerts(monkeypatch):
    alerts = []
    def alert_func(msg: str) -> None:
        alerts.append(msg)
    monitor = mod.Monitor(alert_func)
    monitor.record("something")
    monitor.record("error happened")
    assert alerts == ["error happened"]
