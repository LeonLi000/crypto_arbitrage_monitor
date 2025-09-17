"""Notification helpers for surfacing alerts from the monitoring system."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .logger import get_logger

logger = get_logger(__name__)


class NotificationChannel(Protocol):
    """Interface implemented by notification transports."""

    def send(self, message: str) -> None:
        ...


@dataclass
class ConsoleChannel:
    """Simple stdout based notification channel."""

    prefix: str = "[NOTIFY]"

    def send(self, message: str) -> None:  # pragma: no cover - trivial
        logger.info("%s %s", self.prefix, message)


class Notifier:
    """Dispatch notifications to one or more channels."""

    def __init__(self, channels: list[NotificationChannel] | None = None) -> None:
        self._channels = channels or [ConsoleChannel()]

    def notify(self, message: str) -> None:
        logger.debug("Dispatching notification: %s", message)
        for channel in self._channels:
            try:
                channel.send(message)
            except Exception as exc:  # pragma: no cover - defensive
                logger.exception("Notification dispatch failed: %s", exc)
