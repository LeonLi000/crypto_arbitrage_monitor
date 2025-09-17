"""Utility helpers for application-wide logging configuration."""
from __future__ import annotations

import logging
from logging import Logger
from typing import Optional

_DEFAULT_FORMAT = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"


def setup_logging(level: int = logging.INFO, fmt: str = _DEFAULT_FORMAT) -> None:
    """Configure the global logging settings.

    Args:
        level: Minimum severity level for logs.
        fmt: Log line format string.
    """
    if logging.getLogger().handlers:
        # Avoid adding duplicate handlers when setup is invoked multiple times.
        return

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(fmt))

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(handler)


def get_logger(name: Optional[str] = None) -> Logger:
    """Return a module level logger configured with the global settings."""
    if not logging.getLogger().handlers:
        setup_logging()
    return logging.getLogger(name)
