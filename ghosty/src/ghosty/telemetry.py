"""
Telemetry sidecar — silent background logger writing to a dedicated local file.
Never prints to stdout. (14-step loop requirement #14)
"""

from __future__ import annotations

import logging
from pathlib import Path

_LOG_DIR = Path.home() / ".config" / "ghosty"
_LOG_PATH = _LOG_DIR / "tui_debug.log"

_logger: logging.Logger | None = None


def setup_telemetry() -> logging.Logger:
    """Initialize the telemetry logger. Idempotent — call once at startup."""
    global _logger
    if _logger is not None:
        return _logger

    _LOG_DIR.mkdir(parents=True, exist_ok=True)

    _logger = logging.getLogger("ghosty.telemetry")
    _logger.setLevel(logging.DEBUG)
    _logger.propagate = False  # ponytail: never leak to root logger → stdout

    handler = logging.FileHandler(str(_LOG_PATH), encoding="utf-8")
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    )
    _logger.addHandler(handler)
    return _logger


def log_event(msg: str, level: str = "info") -> None:
    """Log a structured event to the telemetry sidecar."""
    if _logger is None:
        setup_telemetry()
    getattr(_logger, level, _logger.info)(msg)  # type: ignore[union-attr]


def log_exception(exc: Exception, context: str = "") -> None:
    """Log a full exception traceback to the telemetry sidecar."""
    if _logger is None:
        setup_telemetry()
    prefix = f"{context}: " if context else ""
    _logger.exception(f"{prefix}{exc}")  # type: ignore[union-attr]
