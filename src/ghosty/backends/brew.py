"""
Homebrew backend — typed install/uninstall/list with auto-rollback.

Usage:
    backend = BrewBackend()
    op = backend.install("lulu")
    # op comes with op.rollback = brew uninstall lulu
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ghosty.catalog import ActionType, Op

BREW_PATH = Path("/opt/homebrew/bin/brew")


class BrewBackend:
    """Typed wrapper around Homebrew operations with auto-rollback."""

    @staticmethod
    def install(formula: str) -> Op:
        """Install a formula, auto-rollback uninstalls it."""
        return Op(
            shell=str(BREW_PATH),
            args=("install", formula),
            description=f"Install {formula}",
            timeout_s=120,
            idempotent=True,
            rollback=Op(
                shell=str(BREW_PATH),
                args=("uninstall", formula),
                description=f"Rollback: uninstall {formula}",
                timeout_s=60,
            ),
        )

    @staticmethod
    def uninstall(formula: str) -> Op:
        """Uninstall a formula (no rollback — would need reinstall)."""
        return Op(
            shell=str(BREW_PATH),
            args=("uninstall", formula),
            description=f"Uninstall {formula}",
            timeout_s=60,
            idempotent=False,
        )

    @staticmethod
    def info(formula: str) -> Op:
        """Get formula info (audit-only)."""
        return Op(
            shell=str(BREW_PATH),
            args=("info", formula),
            description=f"Info for {formula}",
            idempotent=True,
        )

    @staticmethod
    def list_installed() -> Op:
        """List installed formulae (audit)."""
        return Op(
            shell=str(BREW_PATH),
            args=("list", "--formulae"),
            description="List installed formulae",
            idempotent=True,
        )

    @staticmethod
    def is_installed(formula: str) -> bool:
        """Check if a formula is installed (synchronous)."""
        import subprocess
        try:
            r = subprocess.run(
                [str(BREW_PATH), "list", formula],
                capture_output=True, timeout=10,
            )
            return r.returncode == 0
        except Exception:
            return False

    @staticmethod
    def tap(repo: str) -> Op:
        """Add a tap with auto-rollback."""
        return Op(
            shell=str(BREW_PATH),
            args=("tap", repo),
            description=f"Tap {repo}",
            timeout_s=60,
            idempotent=True,
            rollback=Op(
                shell=str(BREW_PATH),
                args=("untap", repo),
                description=f"Rollback: untap {repo}",
                timeout_s=30,
            ),
        )
