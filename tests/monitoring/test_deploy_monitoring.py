from pathlib import Path
import importlib.util

SCRIPT = Path('tools/scripts/deploy_monitoring.py').resolve()
spec = importlib.util.spec_from_file_location('deploy', SCRIPT)
deploy_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deploy_mod)


def test_deploy_success(tmp_path, monkeypatch):
    monkeypatch.setattr(deploy_mod, 'CONFIG_DIR', tmp_path)
    assert deploy_mod.asyncio.run(deploy_mod.main()) == 0
