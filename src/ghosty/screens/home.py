"""Home / dashboard screen — stats cards + quick action buttons."""

from __future__ import annotations

from typing import ClassVar

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Static

from ghosty.catalog import Catalog, get_cheatsheet_path, parse_cheatsheet


class StatCard(Static):
    """A bordered stat tile with a value and label."""

    def __init__(self, value: str, label: str, accent: str = "#7C5CFF", **kwargs) -> None:  # type: ignore[no-untyped-def]
        self._value = value
        self._label = label
        self._accent = accent
        super().__init__(**kwargs)

    def render(self) -> str:
        return (
            f"\n"
            f"[bold #FFFFFF]{self._value}[/]\n"
            f"[#888BAA]{self._label}[/]"
        )


class HomeScreen(Screen[None]):
    """Landing dashboard with overview stats and quick-start buttons."""

    CSS = """
    #home-root {
        align: center middle;
        width: 100%;
        height: 100%;
    }
    #home-inner {
        width: 70;
        height: auto;
        align: center middle;
    }
    #home-header {
        padding: 0 0 1 0;
        text-align: center;
    }
    #home-header Static {
        text-align: center;
    }
    #stats-row {
        margin: 0 0 1 0;
    }
    .stat-card {
        width: 1fr;
        height: 5;
        border: solid #3D3F5C;
        background: #232541;
        text-align: center;
        margin: 0 1 0 0;
    }
    .stat-card:last-of-type {
        margin-right: 0;
    }
    .stat-card.accent-chapters { border-left: solid #7C5CFF; }
    .stat-card.accent-actions { border-left: solid #22D3EE; }
    .stat-card.accent-run { border-left: solid #34D399; }
    .stat-card.accent-health { border-left: solid #F59E0B; }

    #quick-actions {
        margin: 1 0 1 0;
        width: 100%;
    }
    #quick-actions Horizontal {
        align: center middle;
    }
    Button {
        min-width: 16;
        margin: 0 1 0 0;
    }
    Button:last-of-type {
        margin-right: 0;
    }
    #footer-hint {
        text-align: center;
        color: #6B6E8A;
        width: 100%;
    }
    """

    BINDINGS: ClassVar = [
        ("c", "push_screen('catalog')", "Catalog"),
        ("d", "push_screen('doctor')", "Doctor"),
        ("r", "push_screen('replay')", "History"),
    ]

    def compose(self) -> ComposeResult:
        catalog = self._load_catalog()
        total_actions = sum(len(ch.actions) for ch in catalog.chapters)
        total_chapters = len(catalog.chapters)

        with Vertical(id="home-root"):  # noqa: SIM117
            with Vertical(id="home-inner"):
                # Header
                with Vertical(id="home-header"):
                    yield Static("[bold #7C5CFF]GHOSTY[/]", id="brand")
                    yield Static("[#22D3EE]macOS Privacy & Security[/]")
                    yield Static(
                        f"[#888BAA]v2  ·  {total_actions} actions  ·  {total_chapters} chapters[/]",
                    )

                # Stat cards
                with Horizontal(id="stats-row"):
                    yield StatCard(str(total_chapters), "Chapters", id="stat-chapters", classes="stat-card accent-chapters")
                    yield StatCard(str(total_actions), "Actions", id="stat-actions", classes="stat-card accent-actions")
                    yield StatCard("--", "Last Run", id="stat-last-run", classes="stat-card accent-run")
                    yield StatCard("✓", "System", id="stat-health", classes="stat-card accent-health")

                # Quick action buttons
                with Vertical(id="quick-actions"), Horizontal():
                    yield Button("Browse Catalog", variant="primary", id="btn-catalog")
                    yield Button("Doctor Check", variant="default", id="btn-doctor")
                    yield Button("Run All", variant="success", id="btn-run-all")
                    yield Button("Rollback", variant="error", id="btn-rollback")

                # Footer hint
                yield Static(
                    "[dim]c  Catalog  ·  d  Doctor  ·  r  History  ·  q  Quit  ·  ?  Help[/]",
                    id="footer-hint",
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
