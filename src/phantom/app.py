"""
PhantomApp — the Textual application root.

Routes between screens, applies the Phantom theme, and provides
global keybindings.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer, Header

from phantom.screens.catalog import CatalogScreen
from phantom.screens.detail import DetailScreen
from phantom.screens.doctor import DoctorScreen
from phantom.screens.home import HomeScreen
from phantom.screens.replay import ReplayScreen
from phantom.screens.run import RunScreen


class PhantomApp(App[None]):
    """Apple-grade macOS privacy & security TUI."""

    TITLE = "Phantom"
    SUB_TITLE = "macOS Privacy & Security"
    CSS_PATH = None  # inline styles via compose

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

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()

    def on_mount(self) -> None:
        """Launch directly into the home screen."""
        self.push_screen("home")

    def action_show_help(self) -> None:
        """Show a help overlay."""
        from textual.containers import Vertical
        from textual.screen import ModalScreen
        from textual.widgets import Button, Label, Static

        class HelpOverlay(ModalScreen[None]):
            BINDINGS: ClassVar[list[tuple[str, str]]] = [("escape", "dismiss(None)")]  # type: ignore[assignment]  # ponytail: Textual accepts tuple list

            def compose(self) -> ComposeResult:
                with Vertical(classes="help-container"):
                    yield Static("[bold]Phantom Help[/]", classes="help-title")
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


# Export theme constants for the app
DEFAULT_CATALOG_PATH = Path.home() / "MasterBase" / "privacy" / "MacOS-Privacy-CheatSheet.md"
