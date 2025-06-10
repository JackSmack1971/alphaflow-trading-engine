from __future__ import annotations

"""Base strategy classes."""
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

import pandas as pd

from ..signals.models import Signal


class StrategyError(Exception):
    """Raised when strategy execution fails."""


@dataclass
class BaseStrategy:
    """Strategy interface."""

    name: str
    position_size: Decimal

    def generate_signal(self, data: pd.DataFrame) -> Optional[Signal]:
        """Return trading signal."""
        raise NotImplementedError
