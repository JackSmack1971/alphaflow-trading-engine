from pathlib import Path
import importlib.util

SCRIPT = Path(__file__).resolve().parents[1] / 'tools/scripts/validate_structure.py'

spec = importlib.util.spec_from_file_location('validate_structure', SCRIPT)
validate_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate_module)


def test_validate_structure_success(tmp_path):
    expected_dirs = [
        'services/market-data',
        'services/strategy-engine',
        'services/order-execution',
        'services/risk-manager',
        'services/gateway',
        'shared/proto',
        'shared/schemas',
        'shared/utils',
        'infrastructure/docker',
        'infrastructure/k8s',
        'infrastructure/terraform',
        'tools/scripts',
        'tools/monitoring',
    ]
    for d in expected_dirs:
        (tmp_path / d).mkdir(parents=True, exist_ok=True)
    assert validate_module.validate(tmp_path)


def test_validate_structure_failure(tmp_path):
    assert not validate_module.validate(tmp_path)
