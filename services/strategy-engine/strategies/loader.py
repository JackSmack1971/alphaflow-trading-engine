"""Secure strategy loader with sandboxing."""
from __future__ import annotations

import importlib
import logging
import multiprocessing as mp
import os
import re
from decimal import Decimal
from typing import Any, Dict, Type

from .base import BaseStrategy, StrategyError
from shared.utils.logging_utils import get_logger

_PATH_RE = re.compile(r"^[a-zA-Z0-9_.-]+$")

DEFAULT_ALLOWLIST = {
    "services.strategy-engine.strategies.moving_average.MovingAverageCrossover",
    "services.strategy-engine.strategies.rsi_mean_reversion.RSIMeanReversion",
    "services.strategy-engine.strategies.bollinger_squeeze.BollingerSqueeze",
}

ALLOWLIST = {
    p.strip()
    for p in os.getenv("STRATEGY_ALLOWLIST", "").split(",")
    if p.strip()
} or DEFAULT_ALLOWLIST

logger = get_logger(__name__)


class LoaderError(Exception):
    """Raised when loading strategies fails."""


def _sanitize_params(params: Dict[str, str]) -> Dict[str, Any]:
    sanitized: Dict[str, Any] = {}
    for key, val in params.items():
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
            continue
        try:
            sanitized[key] = Decimal(val)
        except Exception:
            sanitized[key] = val
    return sanitized


class SandboxedStrategy(BaseStrategy):
    """Wrapper that runs strategy in a separate process."""

    def __init__(self, strategy: BaseStrategy, timeout: float = 1.0) -> None:
        super().__init__(name=strategy.name, position_size=strategy.position_size)
        self._strategy = strategy
        self._timeout = timeout

    def generate_signal(self, data: Any) -> Any:
        def _run(q: mp.Queue, df: Any) -> None:
            try:
                q.put(self._strategy.generate_signal(df))
            except Exception as exc:  # pragma: no cover - pass exception
                q.put(exc)

        q: mp.Queue = mp.Queue()
        proc = mp.Process(target=_run, args=(q, data))
        proc.start()
        proc.join(self._timeout)
        if proc.is_alive():
            proc.terminate()
            proc.join()
            raise StrategyError("Execution timed out")
        result = q.get()
        if isinstance(result, Exception):
            raise StrategyError(str(result))
        return result


def load_strategy(
    path: str, name: str, position_size: Decimal, timeout: float = 1.0, **params: str
) -> BaseStrategy:
    """Securely load a whitelisted strategy."""
    if not _PATH_RE.fullmatch(path):
        logger.warning("Rejected invalid path: %s", path)
        raise LoaderError("Invalid path")
    if path not in ALLOWLIST:
        logger.warning("Strategy not allowed: %s", path)
        raise LoaderError("Strategy not allowed")
    try:
        module_name, class_name = path.rsplit(".", 1)
        module = importlib.import_module(module_name)
        cls: Type[BaseStrategy] = getattr(module, class_name)
    except (ImportError, AttributeError) as exc:
        raise LoaderError(str(exc)) from exc
    if not issubclass(cls, BaseStrategy):
        raise LoaderError("Invalid strategy type")
    strat = cls(name, position_size, **_sanitize_params(params))
    logger.info("Loaded strategy %s", path)
    return SandboxedStrategy(strat, timeout)
