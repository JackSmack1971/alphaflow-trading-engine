from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


class AuditLogger:
    """Write audit events to a rotating file."""

    def __init__(self, path: Path, max_bytes: int = 10000, backup_count: int = 5) -> None:
        self._logger = logging.getLogger("audit")
        self._logger.setLevel("INFO")
        handler = RotatingFileHandler(path, maxBytes=max_bytes, backupCount=backup_count)
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)

    def log(self, event: str) -> None:
        """Record an audit event."""
        self._logger.info(event)
