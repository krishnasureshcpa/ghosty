"""Run screen — parallel progress grid showing action execution in real time."""

from __future__ import annotations

import asyncio
from typing import Any, ClassVar

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Button, Static

from ghosty.catalog import Action
from ghosty.runner import ExecResult, ExecStatus, RollbackManager, Runner


class ActionProgress(Static):
    """A single action's progress cell in the grid."""

    action_id: reactive[str] = reactive("")
    status: reactive[str] = reactive("pending")
    elapsed: reactive[str] = reactive("--")

    def __init__(self, action_id: str = "", status: str = "pending", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.action_id = action_id
        self.status = status

    def render(self) -> str:
        icons = {
            "pending": "⏳",
            "running": "▶",
            "completed": "✓",
            "failed": "✗",
            "skipped": "⊘",
            "dry_run": "🔍",
        }
        icon = icons.get(self.status, "•")
        color = {
            "pending": "dim",
            "running": "cyan",
            "completed": "green",
            "failed": "red",
            "skipped": "dim",
            "dry_run": "yellow",
        }.get(self.status, "dim")
        return f"[{color}]{icon} [bold]{self.action_id}[/]  {self.elapsed}[/]"


class RunScreen(Screen[None]):
    """Execute actions with a live parallel progress grid."""

    BINDINGS: ClassVar = [
        ("escape", "go_back", "Back"),
        ("space", "toggle_pause", "Pause/Resume"),
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="run-root"):
            yield Static("[bold]Execution Dashboard[/]", id="run-title", classes="title")
            yield Static("Ready to execute", id="run-status", classes="status-line")

            with Vertical(id="progress-grid", classes="grid"):
                yield Static("[dim]No actions loaded — launch from Catalog[/]")

            with Horizontal(id="run-footer", classes="button-row"):
                yield Button("▶ Start", variant="primary", id="btn-start")
                yield Button("⏸ Pause", variant="default", id="btn-pause", disabled=True)
                yield Button("⬅ Back", variant="default", id="btn-back")

    def run_actions(self, actions: list[Action]) -> None:
        """Load and execute a list of actions."""
        grid = self.query_one("#progress-grid", Vertical)
        grid.remove_children()
        self._cells: dict[str, ActionProgress] = {}
        self._actions = actions

        for action in actions:
            cell = ActionProgress(action_id=action.id, status="pending")
            self._cells[action.id] = cell
            grid.mount(cell)

        self._update_status(f"Loaded {len(actions)} actions — press Start to execute")

    def _update_status(self, text: str) -> None:
        self.query_one("#run-status", Static).update(text)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        if btn_id == "btn-start":
            await self.action_start()
        elif btn_id == "btn-pause":
            self.notify("Pause/resume coming soon")
        elif btn_id == "btn-back":
            self.action_go_back()

    async def action_start(self) -> None:
        if not hasattr(self, "_actions") or not self._actions:
            self.notify("No actions to run", severity="warning")
            return

        # Disable start, enable pause
        self.query_one("#btn-start", Button).disabled = True
        self.query_one("#btn-pause", Button).disabled = False
        self._update_status("Running…")

        def on_progress(action_id: str, status: ExecStatus) -> None:
            if action_id in self._cells:
                cell = self._cells[action_id]
                cell.status = status.value
                if status in (ExecStatus.COMPLETED, ExecStatus.FAILED, ExecStatus.DRY_RUN):
                    cell.elapsed = "done"

        runner = Runner(max_parallel=4, dry_run=False, progress_callback=on_progress)
        results = await runner.run_actions(self._actions)

        completed = sum(1 for r in results.values() if r.status == ExecStatus.COMPLETED)
        failed = sum(1 for r in results.values() if r.status == ExecStatus.FAILED)
        self._update_status(f"Done — {completed} succeeded, {failed} failed")

        self.query_one("#btn-start", Button).disabled = False
        self.query_one("#btn-pause", Button).disabled = True

        # Record rollbacks
        rm = RollbackManager()
        await self._record_rollbacks(rm, self._actions, results)

    async def _record_rollbacks(
        self, rm: RollbackManager, actions: list[Action], results: dict[str, ExecResult]
    ) -> None:
        for action in actions:
            res = results.get(action.id)
            if res and res.status == ExecStatus.COMPLETED:
                await rm.record_execution(action.id, action.ops, action.rollback_ops)

    def action_go_back(self) -> None:
        self.app.pop_screen()
