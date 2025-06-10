"""Risk manager service package."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

PACKAGE = "risk_manager"
package = importlib.util.module_from_spec(importlib.machinery.ModuleSpec(PACKAGE, None))
package.__path__ = [str(Path(__file__).resolve().parent)]
sys.modules[PACKAGE] = package

exceptions_spec = importlib.util.spec_from_file_location(f"{PACKAGE}.exceptions", Path(__file__).resolve().parent / "exceptions.py")
exceptions_mod = importlib.util.module_from_spec(exceptions_spec)
exceptions_spec.loader.exec_module(exceptions_mod)
package.exceptions = exceptions_mod

sys.modules[f"{PACKAGE}.exceptions"] = exceptions_mod
app_spec = importlib.util.spec_from_file_location(
    f"{PACKAGE}.app", Path(__file__).resolve().parent / "app.py"
)
app_mod = importlib.util.module_from_spec(app_spec)
app_spec.loader.exec_module(app_mod)

base_spec = importlib.util.spec_from_file_location(
    f"{PACKAGE}.limits.base", Path(__file__).resolve().parent / "limits" / "base.py"
)
base_mod = importlib.util.module_from_spec(base_spec)
base_spec.loader.exec_module(base_mod)

RiskManager = app_mod.RiskManager
Order = base_mod.Order

__all__ = ["RiskManager", "Order", "exceptions_mod"]
