"""
Explicit message dispatch — MsgX enums for all intra-app communication.

Messages are processed by the dispatcher BEFORE reaching layout/widgets,
enforcing a clear data-flow boundary.
(14-step loop requirement #2: Intent Capture)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Any

from ghosty.catalog import Action, Chapter


class MsgX(StrEnum):
    """All application-level messages, defined as an enum.

    Every screen action, navigation event, and side effect is captured
    here as a named message. No stringly-typed routing.
    """

    # ── Navigation ──────────────────────────────────────────────────
    NAV_HOME = auto()
    NAV_CATALOG = auto()
    NAV_DETAIL = auto()
    NAV_DOCTOR = auto()
    NAV_RUN = auto()
    NAV_REPLAY = auto()
    NAV_BACK = auto()
    NAV_HELP = auto()
    NAV_QUIT = auto()

    # ── Catalog ──────────────────────────────────────────────────────
    CATALOG_SELECT_CHAPTER = auto()
    CATALOG_SELECT_ACTION = auto()
    CATALOG_SEARCH = auto()

    # ── Execution ────────────────────────────────────────────────────
    EXEC_START = auto()
    EXEC_STOP = auto()
    EXEC_PAUSE = auto()
    EXEC_RESUME = auto()
    EXEC_DRY_RUN = auto()
    EXEC_APPLY = auto()
    EXEC_UNDO = auto()
    EXEC_ROLLBACK = auto()
    EXEC_PROGRESS = auto()

    # ── Doctor ───────────────────────────────────────────────────────
    DOCTOR_RUN_CHECKS = auto()
    DOCTOR_REFRESH = auto()

    # ── UI ───────────────────────────────────────────────────────────
    UI_TOGGLE_DARK = auto()
    UI_TOGGLE_SIDEBAR = auto()
    UI_REFRESH = auto()
    UI_DISMISS = auto()


@dataclass(slots=True, frozen=True)
class Msg:
    """A fully-typed application message carrying optional payload."""

    type: MsgX
    chapter: Chapter | None = None
    action: Action | None = None
    payload: str = ""
    data: Any = None

    def __repr__(self) -> str:
        base = f"Msg({self.type.name}"
        if self.action:
            base += f", action={self.action.id}"
        if self.chapter:
            base += f", chapter={self.chapter.title}"
        if self.payload:
            base += f", payload={self.payload}"
        return base + ")"


# Convenience constructors — reduces noise in call sites


def nav(to: str) -> Msg:
    return Msg(type=MsgX[to.upper()] if to.upper() in MsgX.__members__ else MsgX.NAV_HOME)


def select_action(action: Action) -> Msg:
    return Msg(type=MsgX.CATALOG_SELECT_ACTION, action=action)


def select_chapter(chapter: Chapter) -> Msg:
    return Msg(type=MsgX.CATALOG_SELECT_CHAPTER, chapter=chapter)


def exec_cmd(kind: str, *, dry_run: bool = False) -> Msg:
    if kind == "start":
        return Msg(type=MsgX.EXEC_DRY_RUN if dry_run else MsgX.EXEC_START)
    if kind == "undo":
        return Msg(type=MsgX.EXEC_UNDO)
    return Msg(type=MsgX.EXEC_START)
