from importlib import util
from pathlib import Path

SCRIPT = Path('shared/utils/telemetry.py').resolve()
spec = util.spec_from_file_location('telemetry', SCRIPT)
telemetry = util.module_from_spec(spec)
spec.loader.exec_module(telemetry)


def test_setup_tracing():
    telemetry.setup_tracing('test')
    provider = telemetry.trace.get_tracer_provider()
    assert isinstance(provider, telemetry.TracerProvider)
