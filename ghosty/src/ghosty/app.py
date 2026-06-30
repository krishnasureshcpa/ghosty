"""
GhostyApp — the Textual application root.

Routes between screens, applies the Ghosty theme, and provides
global keybindings.
"""

from __future__ import annotations

from typing import Any, ClassVar

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer, Header

from ghosty.catalog import get_cheatsheet_path
from ghosty.screens.catalog import CatalogScreen
from ghosty.screens.detail import DetailScreen
from ghosty.screens.doctor import DoctorScreen
from ghosty.screens.home import HomeScreen
from ghosty.screens.replay import ReplayScreen
from ghosty.screens.run import RunScreen
from ghosty.state import AppState, AppMode, evolve
from ghosty.telemetry import log_event, log_exception, setup_telemetry

_CSS = """
Screen {
    background: #0B0F1A;
    color: #F8FAFC;
}

Header {
    dock: top;
    height: 3;
    background: #0B0F1A;
    color: #7C5CFF;
    border-bottom: solid #22D3EE;
    padding: 0 1;
}

Footer {
    dock: bottom;
    height: 1;
    background: #0B0F1A;
    color: #94A3B8;
    border-top: solid #7C5CFF;
}

/* ── Shared panel styling ──────────────────────────────────────── */
.panel {
    border: solid #94A3B8;
    margin: 0;
    padding: 0 1;
}

.panel-title {
    color: #7C5CFF;
    text-style: bold;
    padding: 0 1;
}

.grid {
    layout: grid;
    grid-size: 2 4;
    grid-gutter: 0;
    margin: 0;
}

.button-row {
    height: 3;
    align: center middle;
    background: #0B0F1A;
    border-top: solid #7C5CFF;
    padding: 0 1;
}

.title {
    color: #7C5CFF;
    text-style: bold;
    padding: 0 1;
    border-bottom: solid #22D3EE;
    height: 3;
}

.status-line {
    color: #94A3B8;
    height: 1;
    padding: 0 1;
}

/* ── Help overlay ──────────────────────────────────────────────── */
.help-container {
    align: center middle;
    width: 40;
    height: auto;
    border: solid #7C5CFF;
    background: #0B0F1A;
    padding: 1 2;
}

.help-title {
    text-style: bold;
    color: #7C5CFF;
    text-align: center;
}
"""


class GhostyApp(App[None]):
    """Apple-grade macOS privacy & security TUI."""

    TITLE = "Ghosty"
    SUB_TITLE = "macOS Privacy & Security"
    CSS = _CSS

    SCREENS: ClassVar[dict[str, type[Screen[Any]]]] = {  # type: ignore[assignment]  # ponytail: Textual accepts dict at runtime
        "home": HomeScreen,
        "catalog": CatalogScreen,
        "detail": DetailScreen,
        "run": RunScreen,
        "doctor": DoctorScreen,
        "replay": ReplayScreen,
    }

    BINDINGS: ClassVar[list[Binding]] = [  # type: ignore[assignment]  # ponytail: Textual accepts list[Binding]
        Binding("h", "push_screen('home')", "Home", show=False),
        Binding("c", "push_screen('catalog')", "Catalog", show=True),
        Binding("d", "push_screen('doctor')", "Doctor", show=True),
        Binding("r", "push_screen('replay')", "History", show=True),
        Binding("q", "quit", "Quit", show=True),
        Binding("question_mark", "show_help", "Help", show=False),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.state = AppState()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()

    def on_mount(self) -> None:
        """Launch directly into the home screen and initialize telemetry."""
        setup_telemetry()
        log_event("GhostyApp mounted")
        self.state = evolve(self.state, mode=AppMode.HOME)
        self.push_screen("home")

    def _handle_exception(self, error: BaseException) -> bool:
        """Graceful panic: log to telemetry, restore terminal, don't crash silently.

        (14-step loop requirement #9)
        """
        log_exception(error, context="GhostyApp._handle_exception")
        return super()._handle_exception(error)

    def action_show_help(self) -> None:
        """Show a help overlay."""
        from textual.containers import Vertical
        from textual.screen import ModalScreen
        from textual.widgets import Button, Label, Static

        class HelpOverlay(ModalScreen[None]):
            BINDINGS: ClassVar[list[tuple[str, str]]] = [("escape", "dismiss(None)")]  # type: ignore[assignment]  # ponytail: Textual accepts tuple list

            def compose(self) -> ComposeResult:
                with Vertical(classes="help-container"):
                    yield Static("[bold]Ghosty Help[/]", classes="help-title")
                    yield Label("c  Catalog browser  |  d  Doctor  |  r  History")
                    yield Label("h  Home  |  q  Quit  |  ?  This help")
                    yield Label("↑/↓  Navigate  |  Enter  Select  |  Esc  Back")
                    yield Button("Dismiss", variant="primary", id="dismiss")

            def on_button_pressed(self, _: Button.Pressed) -> None:
                self.dismiss(None)

        self.push_screen(HelpOverlay())

    def action_toggle_dark(self) -> None:
        """Override to keep dark mode always on."""
        self.dark = True


DEFAULT_CATALOG_PATH = get_cheatsheet_path()
