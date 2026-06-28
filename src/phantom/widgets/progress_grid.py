"""Progress grid — live execution status for multiple actions in parallel."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Grid
from textual.reactive import reactive
from textual.widgets import Static

from phantom.runner import ExecStatus


class ActionProgressCell(Static):
    """A single cell in the progress grid."""

    action_id: reactive[str] = reactive("")
    status: reactive[ExecStatus] = reactive(ExecStatus.PENDING)
    label: reactive[str] = reactive("")

    def render(self) -> str:
        icons = {
            ExecStatus.PENDING: "⏳",
            ExecStatus.RUNNING: "▶",
            ExecStatus.COMPLETED: "✓",
            ExecStatus.FAILED: "✗",
            ExecStatus.SKIPPED: "⊘",
            ExecStatus.DRY_RUN: "🔍",
        }
        colors = {
            ExecStatus.PENDING: "dim",
            ExecStatus.RUNNING: "cyan",
            ExecStatus.COMPLETED: "green",
            ExecStatus.FAILED: "red",
            ExecStatus.SKIPPED: "dim",
            ExecStatus.DRY_RUN: "yellow",
        }
        icon = icons.get(self.status, "•")
        color = colors.get(self.status, "dim")
        return f"[{color}]{icon}  [bold]{self.label}[/][/]"


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
