#!/usr/bin/env python3
"""Validate repository folder structure."""
from pathlib import Path
import sys

EXPECTED_DIRS = [
    "services/market-data",
    "services/strategy-engine",
    "services/order-execution",
    "services/risk-manager",
    "services/gateway",
    "shared/proto",
    "shared/schemas",
    "shared/utils",
    "infrastructure/docker",
    "infrastructure/k8s",
    "infrastructure/terraform",
    "tools/scripts",
    "tools/monitoring",
]

def validate(base_path: Path = Path('.')) -> bool:
    missing = [d for d in EXPECTED_DIRS if not (base_path / d).exists()]
    if missing:
        print("Missing expected directories:")
        for d in missing:
            print(f" - {d}")
        return False
    print("Repository structure validated.")
    return True

if __name__ == "__main__":
    success = validate(Path('.'))
    sys.exit(0 if success else 1)
