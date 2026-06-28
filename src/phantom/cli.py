"""
Phantom CLI — Click entry point.

Usage:
    phantom                       Launch the TUI
    phantom doctor                System health check
    phantom harden all            Non-interactive full hardening
    phantom harden firewall       Single chapter
    phantom snapshot save         Snapshot current state
    phantom snapshot list         List snapshots
    phantom rollback              Undo last action
    phantom rollback 3            Undo last 3 actions
    phantom replay                Show execution history
    phantom install lulu          One-shot brew install + verify
    phantom undo firewall.stealth Undo specific action by ID
    phantom --json                Machine-readable output for all modes
"""

from __future__ import annotations

import asyncio
import json
import sys
from datetime import UTC
from pathlib import Path
from typing import TYPE_CHECKING, Any

import click

if TYPE_CHECKING:
    from phantom.catalog import Action, Catalog
    from phantom.runner import ExecResult

from phantom import __version__
from phantom.catalog import parse_cheatsheet
from phantom.runner import RollbackManager, Runner

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_CHEAT_SHEET = Path.home() / "MasterBase" / "privacy" / "MacOS-Privacy-CheatSheet.md"
_CATALOG_JSON = Path.home() / ".config" / "phantom" / "catalog.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_catalog() -> Catalog:
    """Parse or load cached catalog."""
    if _CATALOG_JSON.exists():
        from phantom.catalog import Catalog

        return Catalog.model_validate_json(_CATALOG_JSON.read_text())
    catalog = parse_cheatsheet(_CHEAT_SHEET)
    _CATALOG_JSON.parent.mkdir(parents=True, exist_ok=True)
    _CATALOG_JSON.write_text(catalog.model_dump_json(indent=2))
    return catalog


def _output(data: dict[str, Any], json_output: bool) -> None:
    if json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        for k, v in data.items():
            click.echo(f"  {k}: {v}")


# ---------------------------------------------------------------------------
# CLI group
# ---------------------------------------------------------------------------


@click.group(invoke_without_command=True)
@click.option("--json", "json_output", is_flag=True, help="Machine-readable JSON output")
@click.option("--version", "show_version", is_flag=True, help="Print version")
@click.pass_context
def cli(ctx: click.Context, json_output: bool, show_version: bool) -> None:
    """Phantom — Apple-grade macOS privacy & security TUI.

    Browse 20+ chapters of curated hardening guidance and execute
    them from a single keyboard-first terminal app.
    """
    if show_version:
        click.echo(f"phantom v{__version__}")
        ctx.exit()

    if ctx.invoked_subcommand is None:
        # Default: launch the TUI
        ctx.invoke(tui)


# ---------------------------------------------------------------------------
# TUI (default)
# ---------------------------------------------------------------------------


@cli.command(name="tui")
def tui() -> None:
    """Launch the Phantom TUI (default)."""
    # Lazy import so Textual is only loaded when needed
    try:
        from phantom.app import PhantomApp
    except ImportError:
        click.secho("TUI not available — install with: uv sync", fg="red")
        sys.exit(1)

    app = PhantomApp()
    app.run()


# ---------------------------------------------------------------------------
# Doctor — system health check
# ---------------------------------------------------------------------------


@cli.command()
@click.option("--json", "json_output", is_flag=True)
def doctor(json_output: bool) -> None:
    """Check system prerequisites and report health."""
    checks: dict[str, str | bool] = {}

    # Apple Silicon
    import platform

    checks["arch"] = platform.machine()
    checks["apple_silicon"] = platform.machine() == "arm64"

    # SIP status
    import subprocess

    try:
        r = subprocess.run(
            ["/usr/bin/csrutil", "status"], capture_output=True, text=True, timeout=5
        )
        checks["sip"] = "enabled" in r.stdout.lower()
        checks["sip_detail"] = r.stdout.strip()
    except Exception as e:
        checks["sip"] = f"error: {e}"

    # FileVault
    try:
        r = subprocess.run(
            ["/usr/bin/fdesetup", "status"], capture_output=True, text=True, timeout=5
        )
        checks["filevault"] = "on" in r.stdout.lower()
        checks["filevault_detail"] = r.stdout.strip()
    except Exception as e:
        checks["filevault"] = f"error: {e}"

    # Firewall
    try:
        r = subprocess.run(
            ["/usr/libexec/ApplicationFirewall/socketfilterfw", "--getglobalstate"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        checks["firewall"] = "enabled" in r.stdout.lower()
    except Exception as e:
        checks["firewall"] = f"error: {e}"

    # brew
    brew_path = Path("/opt/homebrew/bin/brew")
    checks["brew_installed"] = brew_path.exists()

    # sudo
    try:
        r = subprocess.run(["sudo", "-n", "true"], capture_output=True, text=True, timeout=5)
        checks["sudo_nopass"] = r.returncode == 0
    except Exception:
        checks["sudo_nopass"] = False

    # Terminal capability
    from phantom.theme import detect_capability

    checks["color_capability"] = detect_capability().value

    if json_output:
        click.echo(json.dumps(checks, indent=2, default=str))
    else:
        click.secho("┌─ Phantom Doctor ───────────────────────────────┐", bold=True)
        click.secho(f"  Arch:            {checks['arch']}", fg="cyan")
        click.secho(
            f"  Apple Silicon:   {'✓' if checks.get('apple_silicon') else '✗'}",
            fg="green" if checks.get("apple_silicon") else "red",
        )
        click.secho(
            f"  SIP:             {'✓ enabled' if checks.get('sip') else '✗ disabled'}",
            fg="green" if checks.get("sip") else "red",
        )
        click.secho(
            f"  FileVault:       {'✓ on' if checks.get('filevault') else '✗ off'}",
            fg="green" if checks.get("filevault") else "red",
        )
        click.secho(
            f"  Firewall:        {'✓ enabled' if checks.get('firewall') else '✗ disabled'}",
            fg="green" if checks.get("firewall") else "red",
        )
        click.secho(
            f"  Homebrew:        {'✓' if checks.get('brew_installed') else '✗'}",
            fg="green" if checks.get("brew_installed") else "red",
        )
        click.secho(
            f"  Sudo (noask):    {'✓' if checks.get('sudo_nopass') else '✗ (will prompt)'}",
            fg="green" if checks.get("sudo_nopass") else "yellow",
        )
        click.secho(f"  Terminal color:  {checks['color_capability']}", fg="cyan")
        click.secho("└──────────────────────────────────────────────────┘")


# ---------------------------------------------------------------------------
# Harden — execute actions
# ---------------------------------------------------------------------------


@cli.command()
@click.argument("target", default="all")
@click.option("--dry-run/--no-dry-run", default=True, help="Preview without executing")
@click.option("--json", "json_output", is_flag=True)
def harden(target: str, dry_run: bool, json_output: bool) -> None:
    """Execute hardening actions for a chapter or 'all'."""
    catalog = _load_catalog()

    if target == "all":
        actions = [a for ch in catalog.chapters for a in ch.actions]
        chapter_label = "all chapters"
    else:
        matched = [ch for ch in catalog.chapters if target.lower() in ch.title.lower()]
        if not matched:
            click.secho(f"No chapter matching '{target}'", fg="red")
            sys.exit(1)
        actions = [a for ch in matched for a in ch.actions]
        chapter_label = matched[0].title

    click.echo(f" Preparing {len(actions)} actions from {chapter_label}…")
    if dry_run:
        click.echo(" [DRY RUN] No changes will be made.")

    runner = Runner(max_parallel=4, dry_run=dry_run)
    results = asyncio.run(runner.run_actions(actions))
    summary = runner.get_summary()

    _output(summary, json_output)

    if not dry_run:
        rm = RollbackManager()
        asyncio.run(_record_rollbacks(rm, actions, results))


async def _record_rollbacks(
    rm: RollbackManager, actions: list[Action], results: dict[str, ExecResult]
) -> None:
    for action in actions:
        res = results.get(action.id)
        if res and res.status.value == "completed":
            await rm.record_execution(action.id, action.ops, action.rollback_ops)


# ---------------------------------------------------------------------------
# Snapshot — state capture
# ---------------------------------------------------------------------------


@cli.group()
def snapshot() -> None:
    """Manage system state snapshots."""


@snapshot.command(name="save")
@click.option("--json", "json_output", is_flag=True)
def snapshot_save(json_output: bool) -> None:
    """Capture current state of key security settings."""
    import subprocess
    from datetime import datetime

    snap: dict[str, Any] = {
        "timestamp": datetime.now(UTC).isoformat(),
    }
    # FileVault
    try:
        r = subprocess.run(["fdesetup", "status"], capture_output=True, text=True, timeout=5)
        snap["filevault"] = r.stdout.strip()
    except Exception as e:
        snap["filevault"] = str(e)
    # Firewall
    try:
        r = subprocess.run(
            ["/usr/libexec/ApplicationFirewall/socketfilterfw", "--getglobalstate"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        snap["firewall"] = r.stdout.strip()
    except Exception as e:
        snap["firewall"] = str(e)

    # Save
    path = Path.home() / ".config" / "phantom" / "snapshots"
    path.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    snap_file = path / f"snapshot_{ts}.json"
    snap_file.write_text(json.dumps(snap, indent=2))

    if json_output:
        click.echo(json.dumps({"saved_to": str(snap_file)}, indent=2))
    else:
        click.secho(f" Snapshot saved: {snap_file}", fg="cyan")


@snapshot.command(name="list")
def snapshot_list() -> None:
    """List all saved snapshots."""
    snap_dir = Path.home() / ".config" / "phantom" / "snapshots"
    if not snap_dir.exists():
        click.echo(" No snapshots found.")
        return
    snaps = sorted(snap_dir.glob("snapshot_*.json"), reverse=True)
    for snap in snaps[:20]:
        click.echo(f"  {snap.stem.replace('snapshot_', '')}  {snap}")


# ---------------------------------------------------------------------------
# Rollback — undo actions
# ---------------------------------------------------------------------------


@cli.command()
@click.argument("count", default=1, type=int)
@click.option("--json", "json_output", is_flag=True)
def rollback(count: int, json_output: bool) -> None:
    """Rollback the last N executed actions."""
    rm = RollbackManager()
    results = asyncio.run(rm.rollback_last(count))

    if json_output:
        click.echo(
            json.dumps(
                {
                    "rolled_back": count,
                    "results": [
                        {
                            "action_id": r.action_id,
                            "status": r.status.value,
                            "exit_code": r.exit_code,
                        }
                        for r in results
                    ],
                },
                indent=2,
            )
        )
    else:
        click.secho(f" Rolled back {count} action(s)", fg="cyan")
        for r in results:
            status = "✓" if r.exit_code == 0 else "✗"
            click.echo(f"  {status} {r.action_id} (exit {r.exit_code})")


# ---------------------------------------------------------------------------
# Replay — show history
# ---------------------------------------------------------------------------


@cli.command()
@click.option("--json", "json_output", is_flag=True)
def replay(json_output: bool) -> None:
    """Show execution history from rollback store."""
    rm = RollbackManager()
    history = rm.get_history()

    if not history:
        click.echo(" No execution history found.")
        return

    if json_output:
        click.echo(json.dumps(history, indent=2))
    else:
        click.secho(f" Execution history ({len(history)} entries)", bold=True)
        for entry in reversed(history[-20:]):
            click.echo(f"  {entry['timestamp'][:19]}  {entry['action_id']}")


# ---------------------------------------------------------------------------
# Install — one-shot tool install
# ---------------------------------------------------------------------------


@cli.command()
@click.argument("tool")
@click.option("--json", "json_output", is_flag=True)
def install(tool: str, json_output: bool) -> None:
    """Install a security tool via Homebrew."""
    import subprocess

    click.echo(f" Installing {tool}…")
    try:
        r = subprocess.run(
            ["/opt/homebrew/bin/brew", "install", tool],
            capture_output=True,
            text=True,
            timeout=120,
        )
        success = r.returncode == 0
        if json_output:
            click.echo(json.dumps({"tool": tool, "success": success, "output": r.stdout}))
        else:
            if success:
                click.secho(f" ✓ {tool} installed", fg="green")
            else:
                click.secho(f" ✗ {tool} failed: {r.stderr.strip()}", fg="red")
    except subprocess.TimeoutExpired:
        click.secho(f" ✗ {tool} install timed out", fg="red")
    except FileNotFoundError:
        click.secho(" ✗ Homebrew not found at /opt/homebrew/bin/brew", fg="red")


# ---------------------------------------------------------------------------
# Undo — undo specific action
# ---------------------------------------------------------------------------


@cli.command()
@click.argument("action_id")
@click.option("--json", "json_output", is_flag=True)
def undo(action_id: str, json_output: bool) -> None:
    """Undo a specific action by ID (e.g. 'firewall.stealth')."""
    rm = RollbackManager()
    history = rm.get_history()

    matching = [e for e in history if e["action_id"] == action_id]
    if not matching:
        click.secho(f"No history for action '{action_id}'", fg="red")
        return

    click.echo(f" Rolling back {len(matching)} occurrences of {action_id}…")
    results = asyncio.run(rm.rollback_last(len(matching)))

    if json_output:
        click.echo(
            json.dumps(
                {
                    "action_id": action_id,
                    "results": [
                        {"status": r.status.value, "exit_code": r.exit_code} for r in results
                    ],
                },
                indent=2,
            )
        )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
