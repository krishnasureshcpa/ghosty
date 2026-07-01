"""
launchd backend — typed enable/disable/load/unload with auto-rollback.

Usage:
    backend = LaunchctlBackend()
    op = backend.disable("com.apple.mds")
    # op comes with op.rollback = launchctl enable ...
"""

from __future__ import annotations

from ghosty.catalog import Op


class LaunchctlBackend:
    """Typed wrapper around launchctl operations with auto-rollback."""

    @staticmethod
    def disable(service: str) -> Op:
        """Disable a launchd service, auto-rollback re-enables it."""
        return Op(
            shell="launchctl",
            args=("disable", service),
            description=f"Disable {service}",
            requires_sudo=True,
            idempotent=True,
            rollback=Op(
                shell="launchctl",
                args=("enable", service),
                description=f"Rollback: enable {service}",
                requires_sudo=True,
            ),
        )

    @staticmethod
    def enable(service: str) -> Op:
        """Enable a launchd service."""
        return Op(
            shell="launchctl",
            args=("enable", service),
            description=f"Enable {service}",
            requires_sudo=True,
            idempotent=True,
        )

    @staticmethod
    def load(path: str) -> Op:
        """Load a plist, auto-rollback unloads it."""
        return Op(
            shell="launchctl",
            args=("load", path),
            description=f"Load {path}",
            requires_sudo=True,
            idempotent=True,
            rollback=Op(
                shell="launchctl",
                args=("unload", path),
                description=f"Rollback: unload {path}",
                requires_sudo=True,
            ),
        )

    @staticmethod
    def unload(path: str) -> Op:
        """Unload a plist (no rollback — would need load)."""
        return Op(
            shell="launchctl",
            args=("unload", path),
            description=f"Unload {path}",
            requires_sudo=True,
            idempotent=True,
        )

    @staticmethod
    def list() -> Op:
        """List all services (audit)."""
        return Op(
            shell="launchctl",
            args=("list",),
            description="List launchd services",
            idempotent=True,
        )

    @staticmethod
    def print(service: str) -> Op:
        """Print service details (audit)."""
        return Op(
            shell="launchctl",
            args=("print", service),
            description=f"Print {service} status",
            idempotent=True,
        )
