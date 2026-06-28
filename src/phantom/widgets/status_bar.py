"""StatusBar — pinned at bottom, shows current screen + job queue + timer."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static


class StatusBar(Widget):
    """Bottom status bar with context hints."""

    def compose(self) -> ComposeResult:
        yield Static(
            "[bold #7C5CFF]ph[/]#[dim]screen[/]  "
            "[#22D3EE]●[/] idle  "
            "[dim]0 queued[/]  "
            "[dim]---[/]",
            id="status-bar-content",
        )

    def set_screen(self, name: str) -> None:
        self.query_one("#status-bar-content", Static).update(
            f"[bold #7C5CFF]ph[/]#[dim]{name}[/]  "
            f"[#22D3EE]●[/] idle  "
            f"[dim]0 queued[/]  "
            f"[dim]---[/]"
        )

    def set_queue(self, count: int) -> None:
        st = self.query_one("#status-bar-content", Static)
        current = st.renderable or ""
        parts = str(current).split("  ")
        if len(parts) >= 3:
            st.update("  ".join([*parts[:2], f"[dim]{count} queued[/]", *parts[3:]]))

    def set_timer(self, elapsed: str) -> None:
        st = self.query_one("#status-bar-content", Static)
        parts = str(st.renderable).split("  ")
        if len(parts) >= 4:
            parts[-1] = f"[dim]{elapsed}[/]"
            st.update("  ".join(parts))
