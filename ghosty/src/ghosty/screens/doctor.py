"""Doctor screen — system health check with live results."""

from __future__ import annotations

import subprocess
from collections.abc import Callable
from typing import Any, ClassVar

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Button, Static

from ghosty.theme import detect_capability


class CheckRow(Static):
    """A single health check row."""

    label: reactive[str] = reactive("")
    status: reactive[str] = reactive("pending")
    detail: reactive[str] = reactive("")

    def __init__(self, label: str = "", status: str = "pending", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.label = label
        self.status = status

    def render(self) -> str:
        icons = {"pending": "⏳", "pass": "✓", "fail": "✗", "warn": "⚠"}
        icon = icons.get(self.status, "?")
        color = {"pending": "dim", "pass": "green", "fail": "red", "warn": "yellow"}.get(
            self.status, "dim"
        )
        detail_str = f"  [dim]{self.detail}[/]" if self.detail else ""
        return f"  [{color}]{icon}  {self.label}{detail_str}[/]"


class DoctorScreen(Screen[None]):
    """System health dashboard."""

    BINDINGS: ClassVar = [
        ("escape", "go_back", "Back"),
        ("r", "refresh", "Refresh"),
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="doctor-root"):
            yield Static("[bold #22D3EE]🩺  Ghosty Doctor[/]", id="doctor-title", classes="title")
            yield Static(
                "Press [bold]r[/] to run checks", id="doctor-status", classes="status-line"
            )

            with Vertical(id="checks-grid", classes="grid"):
                for check_id in ("arch", "sip", "filevault", "firewall", "brew", "sudo", "color"):
                    yield CheckRow(
                        id=f"check-{check_id}",
                        label=check_id.replace("_", " ").title(),
                        status="pending",
                    )

            with Horizontal(id="doctor-footer", classes="button-row"):
                yield Button("▶ Run Checks", variant="primary", id="btn-run")
                yield Button("⬅ Back", variant="default", id="btn-back")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-run":
            self.action_refresh()
        elif event.button.id == "btn-back":
            self.action_go_back()

    def action_refresh(self) -> None:
        """Run all health checks."""
        self.query_one("#doctor-status", Static).update("Running checks…")
        self.query_one("#btn-run", Button).disabled = True
        self._run_checks()

    def _run_checks(self) -> None:
        import platform

        checks: dict[str, Callable[[], tuple[str, str]]] = {
            "arch": lambda: (
                ("pass", platform.machine())
                if platform.machine() == "arm64"
                else ("warn", platform.machine())
            ),
            "sip": self._check_sip,
            "filevault": self._check_filevault,
            "firewall": self._check_firewall,
            "brew": self._check_brew,
            "sudo": self._check_sudo,
            "color": lambda: ("pass", detect_capability().value),
        }

        for check_id, fn in checks.items():
            try:
                status, detail = fn()
            except Exception as e:
                status, detail = "fail", str(e)
            row = self.query_one(f"#check-{check_id}", CheckRow)
            row.status = status
            row.detail = detail

        self.query_one("#doctor-status", Static).update("All checks complete")
        self.query_one("#btn-run", Button).disabled = False

    @staticmethod
    def _check_sip() -> tuple[str, str]:
        r = subprocess.run(
            ["/usr/bin/csrutil", "status"], capture_output=True, text=True, timeout=5
        )
        return ("pass", "enabled") if "enabled" in r.stdout.lower() else ("fail", r.stdout.strip())

    @staticmethod
    def _check_filevault() -> tuple[str, str]:
        r = subprocess.run(
            ["/usr/bin/fdesetup", "status"], capture_output=True, text=True, timeout=5
        )
        return ("pass", "on") if "on" in r.stdout.lower() else ("fail", r.stdout.strip())

    @staticmethod
    def _check_firewall() -> tuple[str, str]:
        r = subprocess.run(
            ["/usr/libexec/ApplicationFirewall/socketfilterfw", "--getglobalstate"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return ("pass", "enabled") if "enabled" in r.stdout.lower() else ("fail", r.stdout.strip())

    @staticmethod
    def _check_brew() -> tuple[str, str]:
        from pathlib import Path

        brew = Path("/opt/homebrew/bin/brew")
        return ("pass", str(brew)) if brew.exists() else ("fail", "not found")

    @staticmethod
    def _check_sudo() -> tuple[str, str]:
        try:
            r = subprocess.run(["sudo", "-n", "true"], capture_output=True, timeout=5)
            return (
                ("pass", "no password required")
                if r.returncode == 0
                else ("warn", "will prompt for password")
            )
        except Exception:
            return ("warn", "will prompt for password")

    def action_go_back(self) -> None:
        self.app.pop_screen()
