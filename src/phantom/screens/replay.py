"""Replay / History screen — shows execution log and snapshot list."""
from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Label, ListItem, ListView, Static

from phantom.runner import RollbackManager


class ReplayScreen(Screen[None]):
    """View execution history and snapshots."""

    BINDINGS: ClassVar = [
        ("escape", "go_back", "Back"),
        ("r", "refresh", "Refresh"),
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="replay-root"):
            yield Static("[bold]Execution History[/]", id="replay-title", classes="title")

            with Horizontal(id="replay-panels"):
                # History list
                with Vertical(id="history-panel", classes="panel"):
                    yield Static("[bold]Recent Actions[/]", classes="panel-title")
                    yield ListView(id="history-list", classes="history-list")

                # Snapshots
                with Vertical(id="snapshot-panel", classes="panel"):
                    yield Static("[bold]Snapshots[/]", classes="panel-title")
                    yield ListView(id="snapshot-list", classes="snapshot-list")

            with Horizontal(id="replay-footer", classes="button-row"):
                yield Button("🔄 Refresh", variant="primary", id="btn-refresh")
                yield Button("⬅ Back", variant="default", id="btn-back")

    def on_mount(self) -> None:
        self._load_history()
        self._load_snapshots()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-refresh":
            self.action_refresh()
        elif event.button.id == "btn-back":
            self.action_go_back()

    def action_refresh(self) -> None:
        self._load_history()
        self._load_snapshots()
        self.notify("History refreshed")

    def _load_history(self) -> None:
        rm = RollbackManager()
        history = rm.get_history()
        history_list = self.query_one("#history-list", ListView)
        history_list.clear()

        if not history:
            history_list.append(ListItem(Label("[dim]No execution history[/]")))
            return

        for entry in reversed(history[-50:]):
            ts = entry.get("timestamp", "?")[:19]
            aid = entry.get("action_id", "?")
            ops = len(entry.get("ops_executed", []))
            history_list.append(ListItem(
                Label(f"[dim]{ts}[/]  [bold]{aid}[/]  [{ops} ops]"),
            ))

    def _load_snapshots(self) -> None:
        snap_dir = Path.home() / ".config" / "phantom" / "snapshots"
        snap_list = self.query_one("#snapshot-list", ListView)
        snap_list.clear()

        if not snap_dir.exists():
            snap_list.append(ListItem(Label("[dim]No snapshots yet[/]")))
            return

        snaps = sorted(snap_dir.glob("snapshot_*.json"), reverse=True)
        if not snaps:
            snap_list.append(ListItem(Label("[dim]No snapshots yet[/]")))
            return

        for snap in snaps[:20]:
            ts = snap.stem.replace("snapshot_", "")
            size = snap.stat().st_size
            snap_list.append(ListItem(
                Label(f"[dim]{ts}[/]  ({size} bytes)"),
            ))

    def action_go_back(self) -> None:
        self.app.pop_screen()
