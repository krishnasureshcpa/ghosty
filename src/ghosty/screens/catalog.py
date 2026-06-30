"""Catalog screen — chapter tabs + action cards with inline buttons."""

from __future__ import annotations

from typing import Any, ClassVar, Literal

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Input, Label, ListItem, ListView, Static

from ghosty.catalog import Action, Catalog, Chapter, get_cheatsheet_path, parse_cheatsheet


class ActionCard(ListItem):
    """A compact action card with title, description, risk badge, and inline buttons."""

    def __init__(self, action: Action, **kwargs: Any) -> None:
        self._run_btn: Button
        self._dry_btn: Button
        self.action_obj = action
        risk_icon = {3: "🔍", 2: "⚙", 1: "⚠"}
        risk_color = {3: "#22D3EE", 2: "#34D399", 1: "#EF4444"}
        risk_label = {3: "Audit", 2: "Safe", 1: "Destructive"}
        rv = action.risk.value

        icon = risk_icon.get(rv, "•")
        tag_html = f"[bold {risk_color.get(rv, '#888BAA')}]/ {risk_label.get(rv, '?')} \\[/bold]"

        title = Label(f"{icon}  {action.title}  {tag_html}")
        desc = Label(f"[#888BAA]{action.description[:80]}{'…' if len(action.description) > 80 else ''}[/]")

        # We mount buttons separately via catalog to wire events
        self._run_id = f"card-run-{action.id}"
        self._dry_id = f"card-dry-{action.id}"

        self._run_btn = Button("▶ Run", id=self._run_id, classes="small primary", variant="primary")
        self._dry_btn = Button("◇ Dry Run", id=self._dry_id, classes="small", variant="default")

        # Use a static to hold the action reference for event routing
        super().__init__(
            Horizontal(
                Vertical(title, desc),
                Horizontal(self._run_btn, self._dry_btn, id=f"card-btns-{action.id}"),
                id=f"card-{action.id}",
            )
        )


class CatalogScreen(Screen[None]):
    """Browse actions with chapter tabs, search, and inline execution buttons."""

    _dry_task: Any | None = None

    CSS = """
    #catalog-root {
        height: 100%;
    }
    #catalog-top-bar {
        padding: 1 1 0 1;
    }
    #catalog-title {
        text-style: bold;
        color: #7C5CFF;
        padding: 0 0 0 0;
        margin: 0 1 0 0;
    }
    #search-input {
        width: 30;
        margin: 0 0 0 0;
    }
    #chapter-tabs {
        padding: 0 1 0 1;
        height: 3;
        overflow-x: auto;
        overflow-y: hidden;
    }
    .chapter-tab {
        min-width: 10;
        margin: 0 1 0 0;
        padding: 0 2;
    }
    #action-panel {
        height: 1fr;
        padding: 0 1 1 1;
    }
    #action-list {
        height: 100%;
        border: solid #3D3F5C;
        background: #232541;
    }
    #action-list:focus {
        border: solid #7C5CFF;
    }
    ActionCard {
        padding: 0 1;
        height: 4;
    }
    ActionCard:hover {
        background: #2D2F4E;
    }
    ActionCard > Horizontal {
        height: 4;
        align: center middle;
    }
    ActionCard > Horizontal > Vertical:first-of-type {
        width: 1fr;
    }
    ActionCard > Horizontal > Horizontal {
        width: auto;
        align: center middle;
    }
    ActionCard Label {
        padding: 0 0 0 0;
    }
    .empty-state {
        color: #6B6E8A;
        text-align: center;
        width: 100%;
        padding: 2 0;
    }
    #catalog-footer {
        padding: 0 1 1 1;
    }
    #catalog-footer Static {
        color: #6B6E8A;
    }
    #catalog-footer Horizontal {
        align: center middle;
    }
    """

    BINDINGS: ClassVar = [
        ("escape", "go_back", "Back"),
        ("slash", "focus_search", "Search"),
    ]

    catalog: Catalog | None = None
    _current_chapter_idx: int = 0
    _search_text: str = ""

    def compose(self) -> ComposeResult:
        with Vertical(id="catalog-root"):
            # Top bar: title + search
            with Horizontal(id="catalog-top-bar"):
                yield Static("[bold #7C5CFF]⌘  Catalog[/]", id="catalog-title")
                yield Input(placeholder="Search actions…", id="search-input")

            # Chapter tabs
            with Horizontal(id="chapter-tabs"):
                pass  # populated in on_mount

            # Action list panel
            with Vertical(id="action-panel"):
                yield ListView(id="action-list")

            # Footer
            with Horizontal(id="catalog-footer"):
                yield Static("[dim]Enter  Details  ·  Run button executes  ·  /  Search  ·  Esc  Back[/]")

    def on_mount(self) -> None:
        self.catalog = self._load_catalog()
        self._build_chapter_tabs()
        self._show_chapter(0)

    def _load_catalog(self) -> Catalog:
        try:
            return parse_cheatsheet(get_cheatsheet_path())
        except Exception:
            return Catalog()

    def _build_chapter_tabs(self) -> None:
        """Rebuild the chapter tab buttons."""
        container = self.query_one("#chapter-tabs")
        container.remove_children()
        if not self.catalog:
            return
        for idx, ch in enumerate(self.catalog.chapters):
            style: Literal["primary", "default"] = "primary" if idx == self._current_chapter_idx else "default"
            tab = Button(
                f"{ch.number:02d}. {ch.title}",
                id=f"tab-{idx}",
                variant=style,
                classes="chapter-tab",
            )
            container.mount(tab)

    def _show_chapter(self, idx: int) -> None:
        """Display actions for the given chapter index, filtered by search."""
        if not self.catalog or idx >= len(self.catalog.chapters):
            return
        self._current_chapter_idx = idx
        ch = self.catalog.chapters[idx]
        self._render_actions(ch)

    def _render_actions(self, chapter: Chapter) -> None:
        """Populate the action list with filtered cards."""
        action_list = self.query_one("#action-list", ListView)
        action_list.clear()

        actions = chapter.actions
        if self._search_text:
            q = self._search_text.lower()
            actions = [a for a in actions if q in a.title.lower() or q in a.description.lower()]

        if not actions:
            action_list.append(ListItem(Static("[dim]No actions match[/]", classes="empty-state")))
            return

        for action in actions:
            action_list.append(ActionCard(action))

    def on_input_changed(self, event: Input.Changed) -> None:
        """Filter actions as user types."""
        if event.input.id == "search-input":
            self._search_text = event.value
            if self.catalog and self._current_chapter_idx < len(self.catalog.chapters):
                ch = self.catalog.chapters[self._current_chapter_idx]
                self._render_actions(ch)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle chapter tab clicks and inline Run/Dry-Run clicks."""
        btn_id = event.button.id or ""

        # Chapter tab click
        if btn_id.startswith("tab-"):
            idx = int(btn_id.removeprefix("tab-"))
            if idx != self._current_chapter_idx:
                self._current_chapter_idx = idx
                self._build_chapter_tabs()
                self._show_chapter(idx)
            return

        # Inline Run button
        if btn_id.startswith("card-run-"):
            action_id = btn_id.removeprefix("card-run-")
            self._execute_action(action_id)
            return

        # Inline Dry Run button
        if btn_id.startswith("card-dry-"):
            action_id = btn_id.removeprefix("card-dry-")
            self._dry_run_action(action_id)
            return

    def _resolve_action(self, action_id: str) -> Action | None:
        """Find an action by ID across all chapters."""
        if not self.catalog:
            return None
        for ch in self.catalog.chapters:
            for a in ch.actions:
                if a.id == action_id:
                    return a
        return None

    def _execute_action(self, action_id: str) -> None:
        """Push action to run screen for execution."""
        action = self._resolve_action(action_id)
        if not action:
            self.notify(f"Unknown action: {action_id}", severity="error")
            return
        from ghosty.screens.run import RunScreen
        screen = RunScreen()
        screen.run_actions([action])
        self.app.push_screen(screen)

    def _dry_run_action(self, action_id: str) -> None:
        """Dry-run an action inline."""
        action = self._resolve_action(action_id)
        if not action:
            self.notify(f"Unknown action: {action_id}", severity="error")
            return
        import asyncio

        from ghosty.runner import Runner
        async def do_dry() -> None:
            runner = Runner(max_parallel=1, dry_run=True)
            await runner.run_action(action)
            cmd_str = "\n".join(op.command_str() for op in action.ops[:3])
            self.notify(
                f"[DRY RUN] {action.title}\n{cmd_str[:200]}",
                title="Dry Run Complete",
                timeout=8,
            )
        self._dry_task = asyncio.ensure_future(do_dry())

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Navigate to detail screen on Enter."""
        item = event.item
        if isinstance(item, ActionCard):
            from ghosty.screens.detail import DetailScreen
            screen = DetailScreen()
            screen.set_action(item.action_obj)
            self.app.push_screen(screen)

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_focus_search(self) -> None:
        self.query_one("#search-input", Input).focus()
