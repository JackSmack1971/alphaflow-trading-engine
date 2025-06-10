"""Signal generation helpers."""
from __future__ import annotations

from decimal import Decimal
from datetime import datetime

from .models import Signal


def create_signal(action: str, price: Decimal, qty: Decimal) -> Signal:
    """Create a trading signal object."""
    return Signal(timestamp=datetime.utcnow(), action=action, price=price, quantity=qty)
