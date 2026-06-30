"""Progress grid — live execution status for multiple actions in parallel."""

from __future__ import annotations

import time
from typing import Any

from textual.containers import Grid
from textual.reactive import reactive
from textual.widgets import Static

from ghosty.runner import ExecStatus

_SPINNER_CHARS = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"


class ActionProgressCell(Static):
    """A single cell in the progress grid with elapsed tracking."""

    action_id: reactive[str] = reactive("")
    status: reactive[ExecStatus] = reactive(ExecStatus.PENDING)
    label: reactive[str] = reactive("")
    _elapsed: reactive[str] = reactive("")

    def __init__(self, action_id: str = "", label: str = "", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.action_id = action_id
        self.label = label
        self._start_time: float | None = None
        self._spinner_idx = 0

    def on_mount(self) -> None:
        self.set_interval(1 / 10, self._tick_elapsed)

    def _tick_elapsed(self) -> None:
        if self.status != ExecStatus.RUNNING:
            return
        if self._start_time is None:
            return
        elapsed = time.monotonic() - self._start_time
        self._spinner_idx = (self._spinner_idx + 1) % len(_SPINNER_CHARS)
        spinner = _SPINNER_CHARS[self._spinner_idx]
        self._elapsed = f"{spinner} {elapsed:5.1f}s"

    def watch_status(self, old: ExecStatus, new: ExecStatus) -> None:
        if old == ExecStatus.PENDING and new == ExecStatus.RUNNING:
            self._start_time = time.monotonic()
        if new in (ExecStatus.COMPLETED, ExecStatus.FAILED, ExecStatus.SKIPPED):
            self._start_time = None

    def render(self) -> str:
        icons = {
            ExecStatus.PENDING: "○",
            ExecStatus.RUNNING: "○",
            ExecStatus.COMPLETED: "✓",
            ExecStatus.FAILED: "✗",
            ExecStatus.SKIPPED: "⊘",
            ExecStatus.DRY_RUN: "◎",
        }
        colors = {
            ExecStatus.PENDING: "dim",
            ExecStatus.RUNNING: "#22D3EE",
            ExecStatus.COMPLETED: "#22D3EE",
            ExecStatus.FAILED: "#FF5C7C",
            ExecStatus.SKIPPED: "dim",
            ExecStatus.DRY_RUN: "#FFC857",
        }
        icon = icons.get(self.status, "○")
        color = colors.get(self.status, "dim")
        elapsed_str = f"  {self._elapsed}" if self._elapsed else ""
        return f"[{color}]{icon}[/]  [bold]{self.label}[/]{elapsed_str}"


class ProgressGrid(Grid):
    """Grid of action progress cells, one per running action."""

    def add_action(self, action_id: str, label: str) -> ActionProgressCell:
        cell = ActionProgressCell(action_id=action_id, label=label)
        self.mount(cell)
        return cell

    def update_status(self, action_id: str, status: ExecStatus) -> None:
        for child in self.children:
            if isinstance(child, ActionProgressCell) and child.action_id == action_id:
                child.status = status
                break
