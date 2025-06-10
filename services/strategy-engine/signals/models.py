"""Signal models."""
from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime


@dataclass
class Signal:
    """Trading signal."""

    timestamp: datetime
    action: str
    price: Decimal
    quantity: Decimal
