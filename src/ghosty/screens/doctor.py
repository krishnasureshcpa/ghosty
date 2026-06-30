"""Doctor screen — system health check with live-streaming results."""

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
    """A single health check row with animated status."""

    label: reactive[str] = reactive("")
    status: reactive[str] = reactive("pending")
    detail: reactive[str] = reactive("")

    def __init__(self, label: str = "", status: str = "pending", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.label = label
        self.status = status

    def render(self) -> str:
        icons = {"pending": "  ⏳", "running": "  ▶", "pass": "  ✓", "fail": "  ✗", "warn": "  ⚠"}
        icon = icons.get(self.status, "  ?")
        color = {
            "pending": "dim",
            "running": "bold #22D3EE",
            "pass": "bold #34D399",
            "fail": "bold #EF4444",
            "warn": "bold #F59E0B",
        }.get(self.status, "dim")
        detail_str = f"  [#888BAA]{self.detail}[/]" if self.detail else ""
        return f"[{color}]{icon}  {self.label}{detail_str}[/]"


class DoctorScreen(Screen[None]):
    """System health dashboard with live check results."""

    CSS = """
    #doctor-root {
        height: 100%;
        padding: 1;
    }
    #doctor-header {
        padding: 0 0 1 0;
        border-bottom: solid #3D3F5C;
        margin: 0 0 1 0;
    }
    #doctor-title {
        text-style: bold;
        color: #7C5CFF;
    }
    #doctor-status {
        color: #888BAA;
        padding: 0 0 0 0;
    }
    #checks-grid {
        height: 1fr;
        padding: 0 0 0 0;
    }
    CheckRow {
        padding: 0 1;
        height: 3;
        border-bottom: solid #2D2F4E;
    }
    CheckRow:last-of-type {
        border-bottom: none;
    }
    #doctor-footer {
        padding: 1 0 0 0;
        border-top: solid #3D3F5C;
    }
    #doctor-summary {
        color: #BEC1D6;
        margin: 0 0 1 0;
        text-align: center;
    }
    """

    BINDINGS: ClassVar = [
        ("escape", "go_back", "Back"),
        ("r", "run_checks", "Refresh"),
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="doctor-root"):
            with Horizontal(id="doctor-header"):
                yield Static("[bold #7C5CFF]🩺  Doctor[/]", id="doctor-title")
            yield Static("Press [bold]r[/] or [bold]Run Checks[/] to start", id="doctor-status")

            with Vertical(id="checks-grid"):
                for check_id in ("arch", "sip", "filevault", "firewall", "brew", "sudo", "color"):
                    yield CheckRow(
                        id=f"check-{check_id}",
                        label=check_id.replace("_", " ").title(),
                        status="pending",
                    )

            yield Static("", id="doctor-summary")

            with Horizontal(id="doctor-footer"):
                yield Button("▶  Run Checks", variant="primary", id="btn-run")
                yield Button("←  Back", variant="default", id="btn-back")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-run":
            self.run_checks()
        elif event.button.id == "btn-back":
            self.action_go_back()

    def run_checks(self) -> None:
        """Run all health checks with async streaming."""
        self.query_one("#doctor-status", Static).update("[#22D3EE]Running checks…[/]")
        self.query_one("#btn-run", Button).disabled = True
        self.query_one("#doctor-summary", Static).update("")

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

        pass_count = 0
        warn_count = 0
        fail_count = 0

        for check_id, fn in checks.items():
            row = self.query_one(f"#check-{check_id}", CheckRow)
            row.status = "running"
            try:
                status, detail = fn()
            except Exception as e:
                status, detail = "fail", str(e)
            row.status = status
            row.detail = detail
            if status == "pass":
                pass_count += 1
            elif status == "warn":
                warn_count += 1
            elif status == "fail":
                fail_count += 1

        total = len(checks)
        summary_parts = []
        if pass_count:
            summary_parts.append(f"[bold #34D399]{pass_count} passed[/]")
        if warn_count:
            summary_parts.append(f"[bold #F59E0B]{warn_count} warnings[/]")
        if fail_count:
            summary_parts.append(f"[bold #EF4444]{fail_count} failed[/]")

        summary_text = f"[#BEC1D6]—  {'  '.join(summary_parts)}  —  of {total} checks[/]"
        self.query_one("#doctor-summary", Static).update(summary_text)
        self.query_one("#doctor-status", Static).update(
            f"[#34D399]✓ Complete[/]  {summary_text}"
        )
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
