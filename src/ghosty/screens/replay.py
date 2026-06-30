"""Replay / History screen — execution log, snapshots, and rollback."""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar, Any

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Label, ListItem, ListView, Static

from ghosty.runner import RollbackManager


class ReplayScreen(Screen[Any]):
    """View execution history and snapshots with rollback capability."""

    CSS = """
    #replay-root {
        height: 100%;
        padding: 1;
    }
    #replay-header {
        padding: 0 0 1 0;
        border-bottom: solid #3D3F5C;
        margin: 0 0 1 0;
    }
    #replay-title {
        text-style: bold;
        color: #7C5CFF;
    }
    #replay-status {
        color: #888BAA;
        padding: 0 0 0 0;
    }
    #replay-panels {
        height: 1fr;
    }
    .replay-column {
        width: 1fr;
        margin: 0 1 0 0;
    }
    .replay-column:last-of-type {
        margin-right: 0;
    }
    .panel-title {
        text-style: bold;
        color: #22D3EE;
        padding: 0 0 0 0;
    }
    .panel-list {
        height: 1fr;
        border: solid #3D3F5C;
        background: #232541;
    }
    .panel-list:focus {
        border: solid #7C5CFF;
    }
    .replay-item {
        padding: 0 1;
    }
    .replay-item Label {
        padding: 0 0 0 0;
    }
    #replay-footer {
        padding: 1 0 0 0;
        border-top: solid #3D3F5C;
    }
    """

    BINDINGS: ClassVar = [
        ("escape", "go_back", "Back"),
        ("r", "refresh", "Refresh"),
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="replay-root"):
            with Horizontal(id="replay-header"):
                yield Static("[bold #7C5CFF]↩  Execution History[/]", id="replay-title")
            yield Static("Recent actions and snapshots", id="replay-status")

            with Horizontal(id="replay-panels"):
                # History list
                with Vertical(id="history-panel", classes="replay-column"):
                    yield Static("[bold #22D3EE]Recent Actions[/]", classes="panel-title")
                    yield ListView(id="history-list", classes="panel-list")

                # Snapshots
                with Vertical(id="snapshot-panel", classes="replay-column"):
                    yield Static("[bold #34D399]Snapshots[/]", classes="panel-title")
                    yield ListView(id="snapshot-list", classes="panel-list")

            with Horizontal(id="replay-footer"):
                yield Button("🔄  Refresh", variant="primary", id="btn-refresh")
                yield Button("←  Back", variant="default", id="btn-back")

    def on_mount(self) -> None:
        self._load_history()
        self._load_snapshots()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-refresh":
            self._replay_refresh()
        elif event.button.id == "btn-back":
            self.action_go_back()

    def _replay_refresh(self) -> None:
        self._load_history()
        self._load_snapshots()
        self.notify("History refreshed", timeout=2)

    def _load_history(self) -> None:
        rm = RollbackManager()
        history = rm.get_history()
        history_list = self.query_one("#history-list", ListView)
        history_list.clear()

        if not history:
            history_list.append(ListItem(Label("[dim]No execution history yet[/]", classes="replay-item")))
            return

        for entry in reversed(history[-50:]):
            ts = entry.get("timestamp", "?")[:19]
            aid = entry.get("action_id", "?")
            ops = len(entry.get("ops_executed", []))
            item = ListItem(
                Label(f"[#888BAA]{ts}[/]  [bold #E2E8F0]{aid}[/]  [#22D3EE]{ops} ops[/]"),
                classes="replay-item",
            )
            history_list.append(item)

    def _load_snapshots(self) -> None:
        snap_dir = Path.home() / ".config" / "ghosty" / "snapshots"
        snap_list = self.query_one("#snapshot-list", ListView)
        snap_list.clear()

        if not snap_dir.exists():
            snap_list.append(ListItem(Label("[dim]No snapshots yet[/]", classes="replay-item")))
            return

        snaps = sorted(snap_dir.glob("snapshot_*.json"), reverse=True)
        if not snaps:
            snap_list.append(ListItem(Label("[dim]No snapshots yet[/]", classes="replay-item")))
            return

        for snap in snaps[:20]:
            ts = snap.stem.replace("snapshot_", "")
            size = snap.stat().st_size
            item = ListItem(
                Label(f"[#888BAA]{ts}[/]  [#888BAA]({size} bytes)[/]"),
                classes="replay-item",
            )
            snap_list.append(item)

    def action_go_back(self) -> None:
        self.app.pop_screen()
