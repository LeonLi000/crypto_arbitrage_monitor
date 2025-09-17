"""Configuration helpers for loading YAML based settings."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Tuple

try:  # pragma: no cover - optional dependency
    import yaml  # type: ignore
except Exception:  # pragma: no cover - fallback when PyYAML unavailable
    yaml = None

from .logger import get_logger

logger = get_logger(__name__)


@dataclass
class AppConfig:
    """Container for strongly typed application configuration."""

    raw: Dict[str, Any]

    @property
    def monitoring(self) -> Dict[str, Any]:
        return self.raw.get("monitoring", {})

    @property
    def risk(self) -> Dict[str, Any]:
        return self.raw.get("risk", {})

    @property
    def app(self) -> Dict[str, Any]:
        return self.raw.get("app", {})


def load_config(path: str | Path) -> AppConfig:
    logger.debug("Loading configuration from %s", path)
    with open(path, "r", encoding="utf-8") as handle:
        content = handle.read()
    if yaml is not None:
        data = yaml.safe_load(content) or {}
    else:
        data = _parse_simple_yaml(content)
    return AppConfig(raw=data)


def _parse_simple_yaml(text: str) -> Dict[str, Any]:
    """Very small YAML subset parser that handles the provided config file."""

    def coerce(value: str) -> Any:
        if value.lower() in {"true", "false"}:
            return value.lower() == "true"
        try:
            if "." in value:
                return float(value)
            return int(value)
        except ValueError:
            return value.strip('"')

    root: Dict[str, Any] = {}
    stack: list[Tuple[int, Dict[str, Any]]] = [(-1, root)]
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        key_value = line.strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1] if stack else root
        if key_value.endswith(":"):
            key = key_value[:-1].strip()
            new_dict: Dict[str, Any] = {}
            parent[key] = new_dict
            stack.append((indent, new_dict))
        else:
            if ":" not in key_value:
                continue
            key, value = key_value.split(":", 1)
            parent[key.strip()] = coerce(value.strip())
    return root
