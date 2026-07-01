"""
macOS subsystem backends — typed, reversible wrappers around shell commands.

Each backend maps one macOS subsystem (defaults, brew, launchctl, etc.)
into a typed API that produces reversible Ops directly, replacing the
fragile shell-command inference in catalog._infer_rollback().

Usage:
    from ghosty.backends import defaults, brew, launchctl

    op = defaults.write("com.apple.finder", "AppleShowAllFiles", "false")
    # → Op(shell="defaults", args=("write", "com.apple.finder", "AppleShowAllFiles", "false"),
    #     requires_sudo=False, rollback=Op(shell="defaults", args=("delete", ...)))
"""

from ghosty.backends.brew import BrewBackend
from ghosty.backends.defaults import DefaultsBackend
from ghosty.backends.launchctl import LaunchctlBackend
from ghosty.backends.system import SystemBackend

__all__ = [
    "BrewBackend",
    "DefaultsBackend",
    "LaunchctlBackend",
    "SystemBackend",
]
