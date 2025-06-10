from pathlib import Path
import importlib.util

ALERT_SCRIPT = Path('tools/scripts/test_alerts.py').resolve()
spec = importlib.util.spec_from_file_location('alerts', ALERT_SCRIPT)
alerts_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(alerts_mod)


def test_alerts_valid(tmp_path, monkeypatch):
    alerts_file = tmp_path / 'alerts.yaml'
    alerts_file.write_text('- alert: test\n  expr: 1==1')
    monkeypatch.setattr(alerts_mod, 'ALERTS_FILE', alerts_file)
    assert alerts_mod.asyncio.run(alerts_mod.main()) == 0
