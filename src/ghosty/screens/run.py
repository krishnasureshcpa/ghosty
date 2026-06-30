"""Run screen — parallel progress grid showing action execution in real time."""

from __future__ import annotations

from typing import Any, ClassVar

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Button, Static

from ghosty.catalog import Action
from ghosty.runner import ExecStatus, RollbackManager, Runner


class ActionCell(Static):
    """A single action's progress cell with rich visual status."""

    action_id: reactive[str] = reactive("")
    status: reactive[str] = reactive("pending")
    elapsed: reactive[str] = reactive("--")

    def __init__(self, action_id: str = "", title: str = "", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.action_id = action_id
        self._title = title

    def render(self) -> str:
        icons = {
            "pending": "⏳",
            "running": "▶",
            "completed": "✓",
            "failed": "✗",
            "skipped": "⊘",
            "dry_run": "◇",
        }
        icon = icons.get(self.status, "•")
        color = {
            "pending": "dim",
            "running": "bold #22D3EE",
            "completed": "bold #34D399",
            "failed": "bold #EF4444",
            "skipped": "dim",
            "dry_run": "bold #F59E0B",
        }.get(self.status, "dim")
        return f"[{color}]{icon}  {self._title}[/]  [#888BAA]{self.elapsed}[/]"


class RunScreen(Screen[None]):
    """Execute actions with a live parallel progress grid."""

    CSS = """
    #run-root {
        height: 100%;
        padding: 1;
    }
    #run-header {
        padding: 0 0 1 0;
        border-bottom: solid #3D3F5C;
        margin: 0 0 1 0;
    }
    #run-title {
        text-style: bold;
        color: #7C5CFF;
    }
    #run-status {
        color: #888BAA;
        padding: 0 0 0 0;
    }
    #progress-grid {
        height: 1fr;
        padding: 0 0 0 0;
    }
    ActionCell {
        padding: 0 1;
        height: 3;
        border-bottom: solid #2D2F4E;
    }
    ActionCell:last-of-type {
        border-bottom: none;
    }
    #run-footer {
        padding: 1 0 0 0;
        border-top: solid #3D3F5C;
    }
    #run-summary {
        color: #BEC1D6;
        margin: 0 0 1 0;
        text-align: center;
    }
    """

    BINDINGS: ClassVar = [
        ("escape", "go_back", "Back"),
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="run-root"):
            with Horizontal(id="run-header"):
                yield Static("[bold #7C5CFF]▶  Execution Dashboard[/]", id="run-title")
            yield Static("Ready", id="run-status")

            with Vertical(id="progress-grid"):
                yield Static("[dim]No actions loaded[/]")

            yield Static("", id="run-summary")

            with Horizontal(id="run-footer"):
                yield Button("▶  Start", variant="primary", id="btn-start")
                yield Button("←  Back", variant="default", id="btn-back")

    def run_actions(self, actions: list[Action]) -> None:
        """Load actions for execution."""
        grid = self.query_one("#progress-grid", Vertical)
        grid.remove_children()
        self._cells: dict[str, ActionCell] = {}
        self._actions = actions

        for action in actions:
            cell = ActionCell(action_id=action.id, title=action.title, status="pending")
            self._cells[action.id] = cell
            grid.mount(cell)

        self.query_one("#run-status", Static).update(
            f"[#888BAA]Loaded {len(actions)} action{'s' if len(actions) > 1 else ''} — press [bold]Start[/] to execute[/]"
        )
        self.query_one("#run-summary", Static).update("")

    def _update_status(self, text: str) -> None:
        self.query_one("#run-status", Static).update(text)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        if btn_id == "btn-start":
            await self.action_start()
        elif btn_id == "btn-back":
            self.action_go_back()

    async def action_start(self) -> None:
        if not hasattr(self, "_actions") or not self._actions:
            self.notify("No actions to run", severity="warning")
            return

        self.query_one("#btn-start", Button).disabled = True
        self._update_status("[#22D3EE]Running…[/]")

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
        total = len(results)

        summary = f"[#BEC1D6]Done — [bold #34D399]{completed} succeeded[/]"
        if failed:
            summary += f", [bold #EF4444]{failed} failed[/]"
        summary += f"[/] of {total} total"

        self._update_status(summary)
        self.query_one("#run-summary", Static).update(summary)
        self.query_one("#btn-start", Button).disabled = False

        rm = RollbackManager()
        for action in self._actions:
            res = results.get(action.id)
            if res and res.status == ExecStatus.COMPLETED:
                await rm.record_execution(action.id, action.ops, action.rollback_ops)

    def action_go_back(self) -> None:
        self.app.pop_screen()
