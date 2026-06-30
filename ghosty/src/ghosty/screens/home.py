"""Home / dashboard screen — gradient banner, stats, quick actions."""

from __future__ import annotations

from typing import Any, ClassVar

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Button, Static

from ghosty.catalog import Catalog, get_cheatsheet_path, parse_cheatsheet


class StatCard(Static):
    """A single stat tile: number + label."""

    value: reactive[str] = reactive("--")
    label: reactive[str] = reactive("")

    def __init__(self, value: str = "--", label: str = "", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.value = value
        self.label = label

    def render(self) -> str:
        return f"\n[bold]{self.value}[/]\n[dim]{self.label}[/]"


class HomeScreen(Screen[None]):
    """Landing screen with overview stats and quick-start buttons."""

    BINDINGS: ClassVar = [
        ("c", "push_screen('catalog')", "Catalog"),
        ("d", "push_screen('doctor')", "Doctor"),
        ("r", "push_screen('replay')", "History"),
    ]

    def compose(self) -> ComposeResult:
        catalog = self._load_catalog()
        total_actions = sum(len(ch.actions) for ch in catalog.chapters)
        total_chapters = len(catalog.chapters)

        with Vertical(id="home-root"):
            # Banner
            yield Static(
                "[bold #7C5CFF]▚▚  G H O S T Y  ▚▚[/]\n"
                "[#22D3EE]macOS Privacy & Security[/]\n"
                f"[dim]v2 · {total_actions} actions across {total_chapters} chapters[/]",
                id="banner",
            )
            # Stats row
            with Horizontal(id="stats-row", classes="grid"):
                yield StatCard(str(total_chapters), "Chapters", id="stat-chapters")
                yield StatCard(str(total_actions), "Actions", id="stat-actions")
                yield StatCard("--", "Last Run", id="stat-last-run")

            # Quick actions
            with Vertical(id="quick-actions"):
                yield Static("[bold]Quick Actions[/]", classes="section-title")
                with Horizontal(classes="button-row"):
                    yield Button("📋 Browse Catalog", variant="primary", id="btn-catalog")
                    yield Button("🩺 Doctor Check", variant="default", id="btn-doctor")
                    yield Button("▶ Run All", variant="default", id="btn-run-all")
                    yield Button("↺ Rollback", variant="error", id="btn-rollback")

            # Footer hint
            yield Static(
                "[dim]Press [bold]c[/] catalog · [bold]d[/] doctor · [bold]r[/] history · [bold]q[/] quit[/]",
                id="hint",
            )

    def _load_catalog(self) -> Catalog:
        try:
            return parse_cheatsheet(get_cheatsheet_path())
        except Exception:
            return Catalog()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        if btn_id == "btn-catalog":
            self.app.push_screen("catalog")
        elif btn_id == "btn-doctor":
            self.app.push_screen("doctor")
        elif btn_id == "btn-run-all":
            self.app.push_screen("run")
        elif btn_id == "btn-rollback":
            self.app.push_screen("replay")
