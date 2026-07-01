"""
macOS `defaults` backend — typed read/write/delete with auto-rollback.

Replaces the fragile shell-pattern matching in catalog._infer_rollback()
with a typed API that produces correct rollback ops for every operation.

Usage:
    backend = DefaultsBackend()
    op = backend.write("com.apple.finder", "AppleShowAllFiles", "-bool", "true")
    # op comes with op.rollback populated automatically
"""

from __future__ import annotations

from typing import Any

from ghosty.catalog import ActionType, Op


class DefaultsBackend:
    """Typed wrapper around `defaults` read/write/delete with auto-rollback."""

    @staticmethod
    def read(domain: str, key: str) -> Op:
        """Read a defaults key (audit-only)."""
        return Op(
            shell="defaults",
            args=("read", domain, key),
            description=f"Read {domain} {key}",
            idempotent=True,
        )

    @staticmethod
    def write(
        domain: str,
        key: str,
        *,
        type_tag: str | None = None,
        value: str,
    ) -> Op:
        """Write a defaults key with auto-generated rollback.

        Args:
            domain: The domain (e.g. 'com.apple.finder')
            key: The key name
            type_tag: Optional type flag like '-bool', '-int', '-string'
            value: The value to write

        Returns:
            An Op with .rollback automatically populated as 'defaults delete domain key'
        """
        args = ["write", domain, key]
        if type_tag:
            args.append(type_tag)
        args.append(value)

        return Op(
            shell="defaults",
            args=tuple(args),
            description=f"Write {domain} {key} {value}",
            idempotent=True,
            # ponytail: delete is the universal rollback for defaults write
            rollback=Op(
                shell="defaults",
                args=("delete", domain, key),
                description=f"Rollback: delete {domain} {key}",
            ),
        )

    @staticmethod
    def delete(domain: str, key: str) -> Op:
        """Delete a defaults key with no rollback (use with caution)."""
        return Op(
            shell="defaults",
            args=("delete", domain, key),
            description=f"Delete {domain} {key}",
            idempotent=False,
        )

    @staticmethod
    def type_cmd(domain: str, key: str) -> Op:
        """Read the type of a defaults key (audit)."""
        return Op(
            shell="defaults",
            args=("read-type", domain, key),
            description=f"Read type of {domain} {key}",
            idempotent=True,
        )
