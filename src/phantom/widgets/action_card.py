"""ActionCard — compact summary card for a single action (title, risk, ops)."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Button, Label, Static

from phantom.catalog import Action


class ActionCard(Vertical):
    """A compact card showing action info with an Apply button."""

    def __init__(self, action: Action, **kwargs):
        self._action = action
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        risk_icons = {3: "🔍", 2: "⚙", 1: "⚠"}
        risk_icon = risk_icons.get(self._action.risk.value, "•")

        ops_count = len(self._action.ops)
        tag_str = ", ".join(f"#{t}" for t in self._action.tags[:3]) if self._action.tags else ""

        with Vertical(classes="card-border"):
            yield Static(
                f"[bold]{risk_icon}  {self._action.title}[/]\n"
                f"[dim]{self._action.description[:80]}…[/]",
                classes="card-body",
            )
            with Horizontal(classes="card-footer"):
                yield Label(f"[dim]{ops_count} ops[/]", classes="card-meta")
                yield Label(f"[dim]{tag_str}[/]", classes="card-meta")
                yield Button("▶ Apply", variant="primary", classes="card-btn", id=f"apply-{self._action.id}")

    @property
    def action(self) -> Action:
        return self._action
