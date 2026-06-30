"""Detail screen — deep view of a single action with full ops/verify/rollback."""

from __future__ import annotations

from typing import ClassVar

from textual.app import ComposeResult
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.screen import Screen
from textual.widgets import Button, Static

from ghosty.catalog import Action
from ghosty.runner import RollbackManager, Runner


class DetailScreen(Screen[None]):
    """View an action in detail, then execute, dry-run, or roll back."""

    CSS = """
    #detail-root {
        height: 100%;
        padding: 1;
    }
    #detail-header {
        padding: 0 0 1 0;
        border-bottom: solid #3D3F5C;
    }
    #detail-title {
        text-style: bold;
        color: #7C5CFF;
    }
    #detail-desc {
        color: #BEC1D6;
        padding: 1 0 0 0;
    }
    #detail-body {
        height: 1fr;
        padding: 1 0;
    }
    .detail-section {
        padding: 0 0 1 0;
    }
    .detail-section-title {
        text-style: bold;
        color: #22D3EE;
        padding: 0 0 0 0;
    }
    .detail-meta-row {
        padding: 0 0 0 0;
    }
    .detail-meta-row Label {
        padding: 0 1 0 0;
    }
    .code-block {
        background: #1A1B2E;
        color: #34D399;
        padding: 0 1;
        margin: 0 0 0 0;
    }
    #detail-actions {
        padding: 1 0 0 0;
        border-top: solid #3D3F5C;
    }
    """

    BINDINGS: ClassVar = [
        ("escape", "go_back", "Back"),
        ("a", "apply_action", "Apply"),
        ("d", "dry_run_action", "Dry Run"),
        ("u", "undo_action", "Undo"),
    ]

    action: Action | None = None

    def compose(self) -> ComposeResult:
        with Vertical(id="detail-root"):
            with Vertical(id="detail-header"):
                yield Static("[bold]Action Detail[/]", id="detail-title")
                yield Static("", id="detail-desc")

            with ScrollableContainer(id="detail-body"):
                yield Static("Select an action from Catalog", id="detail-content")

            with Horizontal(id="detail-actions"):
                yield Button("▶  Apply", variant="primary", id="btn-apply")
                yield Button("◇  Dry Run", variant="default", id="btn-dry-run")
                yield Button("↩  Undo", variant="error", id="btn-undo", disabled=True)
                yield Button("←  Back", variant="default", id="btn-back")

    def set_action(self, action: Action) -> None:
        """Load an action into this screen."""
        self.action = action

        risk_label = {3: "🔍 Audit", 2: "⚙ Safe", 1: "⚠ Destructive"}
        risk_color = {3: "#22D3EE", 2: "#34D399", 1: "#EF4444"}
        rv = action.risk.value

        ops_lines = []
        for op in action.ops:
            sudo_tag = " [dim #F59E0B](sudo)[/]" if op.requires_sudo else ""
            ops_lines.append(f"  [bold #E2E8F0]$ {op.command_str()}[/]{sudo_tag}")

        ops_text = "\n".join(ops_lines) or "  [dim]No commands[/]"
        verify_text = "\n".join(
            f"  [bold #34D399]✓ {op.command_str()}[/]" for op in action.verify_ops
        ) or "  [dim]No verification[/]"
        rollback_text = "\n".join(
            f"  [bold #F59E0B]↩ {op.command_str()}[/]" for op in action.rollback_ops
        ) or "  [dim]No automatic rollback[/]"

        tags = ", ".join(f"[dim]#{t}[/]" for t in action.tags) if action.tags else "[dim]none[/]"
        deps = ", ".join(action.depends_on) if action.depends_on else "[dim]none[/]"
        reboot = "[bold #F59E0B]⚠ Requires reboot[/]" if action.requires_reboot else ""

        title_html = f"[bold #7C5CFF]{action.title}[/]"
        desc_html = f"{action.description}"

        meta_rows = (
            f"[#888BAA]ID:[/#]  {action.id}\n"
            f"[#888BAA]Risk:[/]  [bold {risk_color.get(rv, '#888BAA')}]{risk_label.get(rv, '?')}[/]\n"
            f"[#888BAA]Type:[/]  {action.type.value}\n"
            f"[#888BAA]Chapter:[/]  {action.chapter}\n"
            f"[#888BAA]Tags:[/]  {tags}\n"
            f"[#888BAA]Depends on:[/]  {deps}\n"
            f"{' ' + reboot if reboot else ''}"
        )

        ops_html = f"[bold #22D3EE]Commands to Execute:[/]\n{ops_text}\n"
        verify_html = f"[bold #34D399]Verification:[/]\n{verify_text}\n"
        rollback_html = f"[bold #F59E0B]Rollback:[/]\n{rollback_text}\n"

        content = f"{meta_rows}\n\n{ops_html}\n{verify_html}\n{rollback_html}"
        self.query_one("#detail-desc", Static).update(desc_html)
        self.query_one("#detail-title", Static).update(title_html)
        self.query_one("#detail-content", Static).update(content)
        self.query_one("#btn-undo", Button).disabled = True

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        if btn_id == "btn-apply":
            self.action_apply_action()
        elif btn_id == "btn-dry-run":
            await self.action_dry_run_action()
        elif btn_id == "btn-undo":
            await self.action_undo_action()
        elif btn_id == "btn-back":
            self.action_go_back()

    async def action_dry_run_action(self) -> None:
        if not self.action:
            return
        runner = Runner(max_parallel=1, dry_run=True)
        await runner.run_action(self.action)
        cmd_str = "\n".join(op.command_str() for op in self.action.ops[:3])
        self.notify(
            f"[DRY RUN] {self.action.title}\n{cmd_str[:200]}",
            title="Dry Run Complete",
            timeout=8,
        )

    def action_apply_action(self) -> None:
        if not self.action:
            return
        from ghosty.screens.run import RunScreen
        screen = RunScreen()
        screen.run_actions([self.action])
        self.app.push_screen(screen)

    async def action_undo_action(self) -> None:
        if not self.action:
            return
        rm = RollbackManager()
        results = await rm.rollback_last(1)
        if results:
            self.notify(f"Rolled back {results[0].action_id}", severity="information")
        else:
            self.notify("Nothing to roll back", severity="warning")

    def action_go_back(self) -> None:
        self.app.pop_screen()
