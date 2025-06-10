from decimal import Decimal
from typing import Optional
import pandas as pd
from importlib import import_module

BaseStrategy = import_module(
    "services.strategy-engine.strategies.base"
).BaseStrategy
Signal = import_module("services.strategy-engine.signals.models").Signal

class HangStrategy(BaseStrategy):
    def __init__(self, name: str, size: Decimal) -> None:
        super().__init__(name, size)

    def generate_signal(self, data: pd.DataFrame) -> Optional[Signal]:
        while True:
            pass
