"""
Unified AppState — single Source of Truth for the entire TUI.
Immutable-at-rest: every mutation produces a new instance.
(14-step loop requirement #1: State Isolation)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from ghosty.catalog import Action, Catalog, Chapter
from ghosty.telemetry import log_event


class AppMode(str, Enum):
    """Top-level mode the application is in."""

    HOME = "home"
    CATALOG = "catalog"
    DETAIL = "detail"
    RUN = "run"
    DOCTOR = "doctor"
    REPLAY = "replay"
    HELP = "help"


@dataclass(slots=True, frozen=True)
class AppState:
    """Immutable Source of Truth.

    Every field is frozen — to "change" state, produce a new instance via
    ``dataclasses.replace()`` or the ``evolve()`` helper below.
    """

    # ── Navigation ──────────────────────────────────────────────────
    mode: AppMode = AppMode.HOME
    previous_mode: AppMode | None = None

    # ── Catalog ─────────────────────────────────────────────────────
    catalog: Catalog | None = None
    current_chapter: Chapter | None = None
    current_action: Action | None = None

    # ── Execution ────────────────────────────────────────────────────
    is_running: bool = False
    is_paused: bool = False
    is_dry_run: bool = True  # safe default
    max_parallel: int = 4
    last_run_summary: dict[str, Any] = field(default_factory=dict)

    # ── UI ───────────────────────────────────────────────────────────
    dark_mode: bool = True
    sidebar_visible: bool = True

    # ── Telemetry ────────────────────────────────────────────────────
    session_started_at: str = ""  # ISO-8601, set once at boot


def evolve(state: AppState, **changes: Any) -> AppState:
    """Produce a new AppState with the given fields changed.

    Logs the transition to the telemetry sidecar.
    """
    mutated = {k: v for k, v in changes.items() if getattr(state, k, object()) != v}
    if mutated:
        log_event(f"AppState evolve: {mutated}")
    return AppState(**{**{f.name: getattr(state, f.name) for f in field(AppState)}, **changes})
