"""ActionCard — compact summary card for a single action (title, risk, ops)."""

from __future__ import annotations

from typing import Any, ClassVar

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Label, Static

from ghosty.catalog import Action


class ActionCard(Vertical):
    """A compact card showing action info with an Apply button."""

    def __init__(self, action: Action, **kwargs: Any) -> None:
        self._action = action
        super().__init__(**kwargs)

    RISK_STYLES: ClassVar[dict[int, str]] = {3: "#22D3EE", 2: "#FFC857", 1: "#FF5C7C"}
    RISK_LABELS: ClassVar[dict[int, str]] = {3: "audit", 2: "safe", 1: "destructive"}

    def compose(self) -> ComposeResult:
        risk_color = self.RISK_STYLES.get(self._action.risk.value, "#94A3B8")
        risk_label = self.RISK_LABELS.get(self._action.risk.value, "?")

        ops_count = len(self._action.ops)
        tag_str = ", ".join(f"#{t}" for t in self._action.tags[:3]) if self._action.tags else ""

        with Vertical(classes="card-border"):
            yield Static(
                f"[bold]{self._action.title}[/]\n"
                f"[dim]{self._action.description[:80]}…[/]",
                classes="card-body",
            )
            with Horizontal(classes="card-footer"):
                yield Label(f"[{risk_color}]{risk_label}[/]", classes="card-meta")
                yield Label(f"[dim]{ops_count} ops[/]", classes="card-meta")
                yield Label(f"[dim]{tag_str}[/]", classes="card-meta")

    @property
    def action(self) -> Action:
        return self._action
