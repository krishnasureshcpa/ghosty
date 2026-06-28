"""Catalog screen — sidebar chapters + action list + preview pane."""
from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Label, ListItem, ListView, Static

from phantom.catalog import Action, Catalog, Chapter, parse_cheatsheet

_CHEAT_SHEET = Path.home() / "MasterBase" / "privacy" / "MacOS-Privacy-CheatSheet.md"


class ActionListItem(ListItem):
    """A single action in the list."""

    def __init__(self, action: Action, **kwargs):
        self.action = action
        risk_icon = {3: "🔍", 2: "⚙", 1: "⚠"}
        icon = risk_icon.get(action.risk.value, "•")
        super().__init__(
            Label(f"{icon} {action.title}"),
            **kwargs,
        )


class CatalogScreen(Screen[None]):
    """Browse chapters and actions with a three-pane layout."""

    BINDINGS: ClassVar = [
        ("escape", "go_back", "Back"),
        ("enter", "select_action", "Select"),
        ("slash", "focus_search", "Search"),
    ]

    catalog: Catalog | None = None
    current_chapter: Chapter | None = None

    def compose(self) -> ComposeResult:
        with Horizontal(id="catalog-root"):
            # Chapter sidebar
            with Vertical(id="sidebar", classes="panel"):
                yield Static("[bold]Chapters[/]", classes="panel-title")
                yield ListView(id="chapter-list", classes="sidebar-list")

            # Action list
            with Vertical(id="middle", classes="panel"):
                yield Static("[bold]Actions[/]", id="action-panel-title", classes="panel-title")
                yield ListView(id="action-list", classes="action-list")

            # Detail preview
            with Vertical(id="preview", classes="panel"):
                yield Static("[bold]Details[/]", classes="panel-title")
                yield Static("Select an action to preview", id="preview-content")

    def on_mount(self) -> None:
        self.catalog = self._load_catalog()
        self._populate_chapters()

    def _load_catalog(self) -> Catalog:
        try:
            return parse_cheatsheet(_CHEAT_SHEET)
        except Exception:
            return Catalog()

    def _populate_chapters(self) -> None:
        chapter_list = self.query_one("#chapter-list", ListView)
        chapter_list.clear()
        if not self.catalog:
            return
        for ch in self.catalog.chapters:
            count = len(ch.actions)
            chapter_list.append(ListItem(
                Label(f"{ch.number:02d}. {ch.title}"),
                Label(f"[dim]{count} actions[/]", classes="badge"),
            ))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle selection in chapter list or action list."""
        list_id = event.list_view.id

        if list_id == "chapter-list":
            self._on_chapter_selected(event)
        elif list_id == "action-list":
            self._on_action_selected(event)

    def _on_chapter_selected(self, event: ListView.Selected) -> None:
        if not self.catalog:
            return
        idx = event.list_view.index
        if idx is None or idx >= len(self.catalog.chapters):
            return
        self.current_chapter = self.catalog.chapters[idx]

        action_list = self.query_one("#action-list", ListView)
        action_list.clear()
        for action in self.current_chapter.actions:
            action_list.append(ActionListItem(action))

        title = self.query_one("#action-panel-title", Static)
        title.update(f"[bold]{self.current_chapter.title}[/]")

    def _on_action_selected(self, event: ListView.Selected) -> None:
        item = event.item
        if not isinstance(item, ActionListItem):
            return
        action = item.action
        preview = self.query_one("#preview-content", Static)
        ops_text = "\n".join(f"  $ {op.command_str()}" for op in action.ops[:5])
        if len(action.ops) > 5:
            ops_text += f"\n  [dim]… and {len(action.ops) - 5} more[/]"
        risk_label = {3: "🔍 Audit", 2: "⚙ Safe", 1: "⚠ Destructive"}
        verify_text = "\n".join(f"  ✓ {op.command_str()}" for op in action.verify_ops[:3]) or "  [dim]none[/]"

        preview.update(
            f"[bold]{action.title}[/]\n\n"
            f"[dim]{action.description}[/]\n\n"
            f"[bold]Risk:[/] {risk_label.get(action.risk.value, '?')}\n"
            f"[bold]Type:[/] {action.type.value}\n"
            f"[bold]Chapter:[/] {action.chapter}\n"
            f"[bold]ID:[/] [dim]{action.id}[/]\n\n"
            f"[bold]Commands:[/]\n{ops_text}\n\n"
            f"[bold]Verify:[/]\n{verify_text}"
        )

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_focus_search(self) -> None:
        self.notify("Type to search actions (coming soon)")
