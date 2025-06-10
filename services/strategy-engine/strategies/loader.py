"""Strategy loader."""
from __future__ import annotations

import importlib
from typing import Any, Type

from .base import BaseStrategy


class LoaderError(Exception):
    """Raised when loading strategies fails."""


def load_strategy(path: str, *args: Any, **kwargs: Any) -> BaseStrategy:
    """Load strategy class from module path."""
    try:
        module_name, class_name = path.rsplit(".", 1)
        module = importlib.import_module(module_name)
        cls: Type[BaseStrategy] = getattr(module, class_name)
        return cls(*args, **kwargs)
    except (ImportError, AttributeError, TypeError) as exc:
        raise LoaderError(str(exc)) from exc
