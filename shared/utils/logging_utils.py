"""Logging helpers."""
import logging
import os
from typing import Optional


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """Return configured logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        level_name = level or os.getenv("LOG_LEVEL", "INFO")
        logger.setLevel(level_name)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
