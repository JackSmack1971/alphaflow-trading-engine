"""Decimal helpers."""
from decimal import Decimal, getcontext
from typing import Union

getcontext().prec = 18


def to_decimal(value: Union[str, float, Decimal]) -> Decimal:
    """Convert input to Decimal with string conversion."""
    return Decimal(str(value))
