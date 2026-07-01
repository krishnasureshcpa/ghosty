"""
System utilities backend — fdesetup, csrutil, socketfilterfw, pfctl, etc.

Provides typed, reversible Ops for the core macOS security subsystems
that ghosty manages. Unifies the duplicated check logic between
cli.py (CLI doctor) and screens/doctor.py (TUI doctor).

Usage:
    backend = SystemBackend()
    ops = [
        backend.fdesetup_status(),
        backend.sip_status(),
        backend.firewall_enable(),
        backend.firewall_stealth_on(),
    ]
"""

from __future__ import annotations

from ghosty.catalog import ActionType, Op


class SystemBackend:
    """Typed wrapper around macOS security subsystem commands."""

    # ── Firewall ──────────────────────────────────────────────────────

    @staticmethod
    def firewall_enable() -> Op:
        return Op(
            shell="/usr/libexec/ApplicationFirewall/socketfilterfw",
            args=("--setglobalstate", "on"),
            description="Enable firewall",
            requires_sudo=True,
            idempotent=True,
            rollback=Op(
                shell="/usr/libexec/ApplicationFirewall/socketfilterfw",
                args=("--setglobalstate", "off"),
                description="Rollback: disable firewall",
                requires_sudo=True,
            ),
        )

    @staticmethod
    def firewall_disable() -> Op:
        return Op(
            shell="/usr/libexec/ApplicationFirewall/socketfilterfw",
            args=("--setglobalstate", "off"),
            description="Disable firewall",
            requires_sudo=True,
            idempotent=True,
        )

    @staticmethod
    def firewall_stealth_on() -> Op:
        return Op(
            shell="/usr/libexec/ApplicationFirewall/socketfilterfw",
            args=("--setstealthmode", "on"),
            description="Enable stealth mode",
            requires_sudo=True,
            idempotent=True,
            rollback=Op(
                shell="/usr/libexec/ApplicationFirewall/socketfilterfw",
                args=("--setstealthmode", "off"),
                description="Rollback: disable stealth mode",
                requires_sudo=True,
            ),
        )

    @staticmethod
    def firewall_status() -> Op:
        return Op(
            shell="/usr/libexec/ApplicationFirewall/socketfilterfw",
            args=("--getglobalstate",),
            description="Check firewall status",
            idempotent=True,
        )

    @staticmethod
    def firewall_stealth_status() -> Op:
        return Op(
            shell="/usr/libexec/ApplicationFirewall/socketfilterfw",
            args=("--getstealthmode",),
            description="Check stealth mode status",
            idempotent=True,
        )

    # ── FileVault ─────────────────────────────────────────────────────

    @staticmethod
    def filevault_enable() -> Op:
        # FileVault disable is complex; no auto-rollback
        return Op(
            shell="fdesetup",
            args=("enable",),
            description="Enable FileVault full-disk encryption",
            requires_sudo=True,
            timeout_s=300,
            idempotent=True,
        )

    @staticmethod
    def filevault_status() -> Op:
        return Op(
            shell="fdesetup",
            args=("status",),
            description="Check FileVault status",
            idempotent=True,
        )

    # ── SIP (System Integrity Protection) ─────────────────────────────

    @staticmethod
    def sip_status() -> Op:
        return Op(
            shell="/usr/bin/csrutil",
            args=("status",),
            description="Check SIP status",
            idempotent=True,
        )

    # ── pf (Packet Filter) ────────────────────────────────────────────

    @staticmethod
    def pf_enable() -> Op:
        return Op(
            shell="pfctl",
            args=("-e",),
            description="Enable pf firewall",
            requires_sudo=True,
            rollback=Op(
                shell="pfctl",
                args=("-d",),
                description="Rollback: disable pf",
                requires_sudo=True,
            ),
        )

    @staticmethod
    def pf_disable() -> Op:
        return Op(
            shell="pfctl",
            args=("-d",),
            description="Disable pf firewall",
            requires_sudo=True,
        )

    @staticmethod
    def pf_load(anchor_file: str = "/etc/pf.anchors/ghosty") -> Op:
        op = Op(
            shell="pfctl",
            args=("-f", anchor_file),
            description=f"Load pf rules from {anchor_file}",
            requires_sudo=True,
            idempotent=True,
        )
        return op

    # ── Software Update ──────────────────────────────────────────────

    @staticmethod
    def software_update_check() -> Op:
        return Op(
            shell="softwareupdate",
            args=("--list",),
            description="Check for available updates",
            timeout_s=60,
            idempotent=True,
        )

    @staticmethod
    def software_update_install() -> Op:
        return Op(
            shell="softwareupdate",
            args=("--install", "--all"),
            description="Install all available updates",
            requires_sudo=True,
            timeout_s=600,
        )

    # ── macOS version / platform info ─────────────────────────────────

    @staticmethod
    def sw_vers() -> Op:
        return Op(
            shell="sw_vers",
            args=(),
            description="Get macOS version info",
            idempotent=True,
        )
