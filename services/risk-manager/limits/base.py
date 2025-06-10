"""Base limit definitions."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from ..monitors.portfolio import Portfolio


@dataclass
class Order:
    """Order representation."""

    symbol: str
    quantity: Decimal
    price: Decimal
    side: str


class BaseLimit(ABC):
    """Interface for all risk limits."""

    @abstractmethod
    def check(self, order: Order, portfolio: Portfolio) -> Optional[str]:
        """Return reason string if breached."""

