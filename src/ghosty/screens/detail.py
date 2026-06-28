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
    """View an action in detail, then execute or roll back."""

    BINDINGS: ClassVar = [
        ("escape", "go_back", "Back"),
        ("a", "apply_action", "Apply"),
        ("d", "dry_run_action", "Dry Run"),
        ("u", "undo_action", "Undo"),
    ]

    action: Action | None = None

    def compose(self) -> ComposeResult:
        with Vertical(id="detail-root"):
            yield Static("[bold]Action Detail[/]", id="detail-title", classes="title")
            with ScrollableContainer(id="detail-body"):
                yield Static("Select an action from Catalog", id="detail-content")
            with Horizontal(id="detail-actions", classes="button-row"):
                yield Button("▶ Apply", variant="primary", id="btn-apply")
                yield Button("🔍 Dry Run", variant="default", id="btn-dry-run")
                yield Button("↩ Undo", variant="error", id="btn-undo", disabled=True)
                yield Button("← Back", variant="default", id="btn-back")

    def set_action(self, action: Action) -> None:
        """Load an action into this screen."""
        self.action = action

        risk_label = {3: "🔍 Audit", 2: "⚙ Safe", 1: "⚠ Destructive"}
        ops_text = (
            "\n".join(
                f"[bold]  $ {op.command_str()}[/]" + (" [dim](sudo)[/]" if op.requires_sudo else "")
                for op in action.ops
            )
            or "  [dim]No commands[/]"
        )

        verify_text = (
            "\n".join(f"  ✓ {op.command_str()}" for op in action.verify_ops)
            or "  [dim]No verification[/]"
        )

        rollback_text = (
            "\n".join(f"  ↩ {op.command_str()}" for op in action.rollback_ops)
            or "  [dim]No automatic rollback[/]"
        )

        tags = ", ".join(f"[dim]#{t}[/]" for t in action.tags) if action.tags else "[dim]none[/]"

        reboot = "⚠ Requires reboot" if action.requires_reboot else ""
        deps = ", ".join(action.depends_on) if action.depends_on else "none"

        content = (
            f"[bold #7C5CFF]{action.title}[/]\n\n"
            f"[dim]{action.description}[/]\n\n"
            f"[bold]ID:[/] {action.id}\n"
            f"[bold]Risk:[/] {risk_label.get(action.risk.value, '?')}\n"
            f"[bold]Type:[/] {action.type.value}\n"
            f"[bold]Chapter:[/] {action.chapter}\n"
            f"[bold]Tags:[/] {tags}\n"
            f"[bold]Depends on:[/] {deps}\n"
            f"{reboot}\n\n"
            f"[bold #22D3EE]Ops (mutate):[/]\n{ops_text}\n\n"
            f"[bold #FFC857]Verify:[/]\n{verify_text}\n\n"
            f"[bold #FF5C7C]Rollback:[/]\n{rollback_text}\n"
        )
        self.query_one("#detail-content", Static).update(content)

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
        result = await runner.run_action(self.action)
        self.notify(
            f"[DRY RUN] {self.action.title}\n{result.stdout[:200]}",
            title="Dry Run Complete",
            timeout=5,
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
