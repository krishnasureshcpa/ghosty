"""
GhostyApp — the Textual application root with full-screen CSS theme.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, ClassVar

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer

from ghosty.screens.catalog import CatalogScreen
from ghosty.screens.detail import DetailScreen
from ghosty.screens.doctor import DoctorScreen
from ghosty.screens.home import HomeScreen
from ghosty.screens.replay import ReplayScreen
from ghosty.screens.run import RunScreen

CSS = """
/* ── Root ──────────────────────────────────── */
Screen {
    background: #1A1B2E;
    color: #E2E8F0;
}
Vertical {
    background: transparent;
}
Horizontal {
    background: transparent;
}

/* ── Panels ────────────────────────────────── */
.panel {
    background: #232541;
    border: solid #3D3F5C;
    padding: 1 2;
}
.panel:focus-within {
    border: solid #7C5CFF;
}

/* ── Headers & Titles ──────────────────────── */
.title {
    text-style: bold;
    color: #E2E8F0;
    padding: 0 0 1 0;
}
.page-title {
    text-style: bold;
    color: #7C5CFF;
    padding: 0 0 1 0;
    text-align: center;
}

/* ── Buttons ───────────────────────────────── */
Button {
    min-width: 14;
    padding: 0 2;
    margin: 0 1 0 0;
}
Button:hover {
    text-style: bold;
}
Button.primary {
    background: #7C5CFF;
    color: #FFFFFF;
}
Button.success {
    background: #34D399;
    color: #1A1B2E;
}
Button.error {
    background: #EF4444;
    color: #FFFFFF;
}
Button.warning {
    background: #F59E0B;
    color: #1A1B2E;
}
Button.small {
    min-width: 8;
    padding: 0 1;
}

/* ── Input ─────────────────────────────────── */
Input {
    background: #232541;
    color: #E2E8F0;
    border: solid #3D3F5C;
}
Input:focus {
    border: solid #7C5CFF;
}

/* ── ListViews ─────────────────────────────── */
ListView {
    background: #232541;
    border: solid #3D3F5C;
    padding: 0;
}
ListView:focus {
    border: solid #7C5CFF;
}
ListItem {
    padding: 0 1;
}
ListItem:hover {
    background: #2D2F4E;
}
ListItem > Horizontal {
    height: 3;
}

/* ── Status line ───────────────────────────── */
.status-line {
    color: #888BAA;
    padding: 0 0 1 0;
}

/* ── Footer ────────────────────────────────── */
Footer {
    background: #232541;
    color: #888BAA;
}

/* ── Grid containers ───────────────────────── */
.grid {
    margin: 1 0;
}

/* ── Tab button styling ────────────────────── */
.tab-active {
    background: #7C5CFF;
    color: #FFFFFF;
    min-width: 10;
}
.tab-inactive {
    background: #2D2F4E;
    color: #888BAA;
    min-width: 10;
}

/* ── Error / warning text ──────────────────── */
.text-error { color: #EF4444; }
.text-success { color: #34D399; }
.text-warning { color: #F59E0B; }
.text-info { color: #22D3EE; }
.text-dim { color: #6B6E8A; }
"""


class GhostyApp(App[None]):
    """Apple-grade macOS privacy & security TUI."""

    TITLE = "Ghosty"
    SUB_TITLE = "macOS Privacy & Security"
    CSS = CSS

    SCREENS: ClassVar[Mapping[str, type[Screen[Any]]]] = {  # type: ignore[assignment]
        "home": HomeScreen,
        "catalog": CatalogScreen,
        "detail": DetailScreen,
        "run": RunScreen,
        "doctor": DoctorScreen,
        "replay": ReplayScreen,
    }

    BINDINGS: ClassVar[list[Binding]] = [  # type: ignore[assignment]
        Binding("h", "push_screen('home')", "Home", show=False),
        Binding("c", "push_screen('catalog')", "Catalog", show=True),
        Binding("d", "push_screen('doctor')", "Doctor", show=True),
        Binding("r", "push_screen('replay')", "History", show=True),
        Binding("q", "quit", "Quit", show=True),
        Binding("question_mark", "show_help", "Help", show=False),
    ]

    def compose(self) -> ComposeResult:
        yield Footer()

    def on_mount(self) -> None:
        self.push_screen("home")

    def action_show_help(self) -> None:
        """Show a styled help overlay."""
        from textual.containers import Vertical
        from textual.screen import ModalScreen
        from textual.widgets import Button, Label

        class HelpOverlay(ModalScreen[None]):
            CSS = """
            HelpOverlay { background: rgba(0,0,0,0.7); align: center middle; }
            #help-box {
                width: 52; height: auto;
                background: #232541; border: solid #7C5CFF;
                padding: 2 3;
            }
            #help-title { text-style: bold; color: #7C5CFF; padding: 0 0 1 0; text-align: center; }
            Label { padding: 0 0 0 0; color: #BEC1D6; }
            #dismiss { width: 20; margin: 1 0 0 0; }
            """
            BINDINGS: ClassVar = [("escape", "dismiss(None)")]

            def compose(self) -> ComposeResult:
                with Vertical(id="help-box"):
                    yield Label("[bold #7C5CFF]Ghosty Help[/]", id="help-title")
                    yield Label("[bold]c[/]  — Browse catalog    [bold]d[/]  — Doctor checks")
                    yield Label("[bold]r[/]  — Execution history [bold]h[/]  — Home screen")
                    yield Label("[bold]q[/]  — Quit              [bold]?[/]  — This help")
                    yield Label("")
                    yield Label("[bold]↑/↓[/]  — Navigate  [bold]Enter[/]  — Select  [bold]Esc[/]  — Back")
                    yield Label("[bold]Tab[/]   — Focus next        [bold]Space[/] — Toggle / Activate")
                    yield Button("Got it", variant="primary", id="dismiss")

            def on_button_pressed(self, _: Button.Pressed) -> None:
                self.dismiss(None)

        self.push_screen(HelpOverlay())

    def action_toggle_dark(self) -> None:
        self.dark = True
