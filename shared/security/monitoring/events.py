from __future__ import annotations

import logging
from typing import Callable


class Monitor:
    """Simple security event monitor."""

    def __init__(self, alert_func: Callable[[str], None]) -> None:
        self._alert = alert_func
        self._logger = logging.getLogger("security.monitor")

    def record(self, event: str) -> None:
        """Record and alert on suspicious events."""
        self._logger.debug(event)
        if "error" in event.lower():
            self._alert(event)
