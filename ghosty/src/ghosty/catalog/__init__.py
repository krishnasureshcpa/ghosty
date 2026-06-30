"""
Catalog parser — transforms the macOS Privacy & Security CheatSheet
into a typed, reversible action graph.

Each chapter (## N · Title) yields multiple Actions, ranked by "paranoid level"
3/2/1 where 3 = read-only/audit, 2 = safe mutate, 1 = destructive/high-impact.
"""

from __future__ import annotations

import hashlib
import os
import re
from datetime import UTC, datetime
from enum import IntEnum, StrEnum
from pathlib import Path

from pydantic import BaseModel, Field, field_validator


class RiskLevel(IntEnum):
    """Paranoid level from the cheat sheet — 3 = audit, 2 = safe, 1 = destructive."""

    AUDIT = 3  # read-only, zero risk (e.g., `fdesetup status`)
    SAFE = 2  # idempotent, easily reversible (e.g., `defaults write …`)
    DESTRUCTIVE = 1  # needs sudo, may break things (e.g., `pfctl -e`)


class ActionType(StrEnum):
    """What kind of operation this action performs."""

    READ = "read"  # query current state
    MUTATE = "mutate"  # change system state
    VERIFY = "verify"  # post-condition check
    INSTALL = "install"  # brew / curl / dmg install
    ROLLBACK = "rollback"  # inverse of mutate


class Op(BaseModel):
    """A single shell operation with metadata for the runner."""

    shell: str
    args: tuple[str, ...] = ()
    capture: bool = True
    timeout_s: int = 30
    requires_sudo: bool = False
    description: str = ""
    idempotent: bool = True

    def command_str(self) -> str:
        return " ".join([self.shell, *self.args])


class Action(BaseModel):
    """An atomic, reversible hardening action."""

    id: str = Field(pattern=r"^[a-z0-9.]+$")  # e.g., "firewall.stealth"
    chapter: str
    chapter_num: int
    title: str
    risk: RiskLevel
    type: ActionType
    description: str
    ops: list[Op] = Field(default_factory=list)
    verify_ops: list[Op] = Field(default_factory=list)
    rollback_ops: list[Op] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    requires_reboot: bool = False
    depends_on: list[str] = Field(default_factory=list)  # action IDs

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        if not re.match(r"^[a-z0-9.]+$", v):
            raise ValueError("id must be lowercase alphanumeric with dots")
        return v


class Chapter(BaseModel):
    """A cheat-sheet chapter containing multiple actions."""

    number: int
    title: str
    summary: str
    actions: list[Action] = Field(default_factory=list)


class Catalog(BaseModel):
    """Complete parsed catalog — serializable to JSON for the TUI."""

    chapters: list[Chapter] = Field(default_factory=list)
    source_hash: str = ""
    generated_at: str = ""

    def get_action(self, action_id: str) -> Action | None:
        for ch in self.chapters:
            for a in ch.actions:
                if a.id == action_id:
                    return a
        return None

    def actions_by_risk(self, risk: RiskLevel) -> list[Action]:
        return [a for ch in self.chapters for a in ch.actions if a.risk == risk]

    def actions_by_tag(self, tag: str) -> list[Action]:
        return [a for ch in self.chapters for a in ch.actions if tag in a.tags]


# ---------------------------------------------------------------------------
# Parser — extracts actions from the markdown cheat sheet
# ---------------------------------------------------------------------------

_HEADING_RE = re.compile(r"^##\s+(\d+)\s*\xb7\s*(.+)$", re.MULTILINE)
_CODE_RE = re.compile(r"```bash\n(.*?)\n```", re.DOTALL)
_LEVEL_RE = re.compile(r"^\*\*(\d+)\s*[·•]\s*(.+?)\*\*$", re.MULTILINE)


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", ".", text.lower()).strip(".")


def _first_sentence(text: str) -> str | None:
    """Extract the first non-empty sentence from text."""
    for line in text.split("\n"):
        line = line.strip()
        if line and not line.startswith("#") and not line.startswith(">"):
            # Find first sentence ending
            for end in (". ", "? ", "! "):
                if end in line:
                    return line.split(end)[0] + end[0]
            return line[:120]
    return None


def _extract_section(text: str, marker: str) -> str | None:
    """Extract text after a marker (case-insensitive)."""
    idx = text.lower().find(marker.lower())
    if idx >= 0:
        return text[idx:]
    return None


def parse_cheatsheet(path: Path) -> Catalog:
    """Parse the full cheat sheet into a structured Catalog."""
    text = path.read_text(encoding="utf-8")
    chapters: list[Chapter] = []

    # Split by chapter headings
    parts = _HEADING_RE.split(text)
    # parts[0] is preamble, then [num, title, body, num, title, body, ...]
    for i in range(1, len(parts), 3):
        num = int(parts[i])
        title = parts[i + 1].strip()
        body = parts[i + 2] if i + 2 < len(parts) else ""

        actions = _parse_chapter_body(num, title, body)
        chapters.append(
            Chapter(
                number=num, title=title, summary=_first_sentence(body) or title, actions=actions
            )
        )

    # Add Quick-Start as pseudo-chapter 21
    quick_start_body = _extract_section(text, "## Quick-Start")
    if quick_start_body:
        qs_actions = _parse_chapter_body(21, "Quick-Start: One-Minute Hardening", quick_start_body)
        # If no actions found (no **N · headers), manually create the 4 quick-start actions
        if not qs_actions:
            qs_actions = _create_quick_start_actions()
        chapters.append(
            Chapter(
                number=21,
                title="Quick-Start",
                summary="Four essential commands",
                actions=qs_actions,
            )
        )

    return Catalog(
        chapters=chapters,
        source_hash=_hash_file(path),
        generated_at=_now_iso(),
    )


def _create_quick_start_actions() -> list[Action]:
    """Manually create the 4 quick-start actions since they lack level headers."""
    return [
        Action(
            id="quickstart.firewall.stealth.01",
            chapter="21 · Quick-Start",
            chapter_num=21,
            title="Enable firewall + stealth mode",
            risk=RiskLevel.SAFE,
            type=ActionType.MUTATE,
            description="Enable the Application Layer Firewall with stealth mode",
            ops=[
                Op(
                    shell="/usr/libexec/ApplicationFirewall/socketfilterfw",
                    args=("--setglobalstate", "on"),
                    requires_sudo=True,
                    description="Enable firewall",
                ),
                Op(
                    shell="/usr/libexec/ApplicationFirewall/socketfilterfw",
                    args=("--setstealthmode", "on"),
                    requires_sudo=True,
                    description="Enable stealth mode",
                ),
                Op(
                    shell="pkill",
                    args=("-HUP", "socketfilterfw"),
                    requires_sudo=True,
                    description="Restart firewall",
                ),
            ],
            verify_ops=[
                Op(
                    shell="/usr/libexec/ApplicationFirewall/socketfilterfw",
                    args=("--getglobalstate",),
                    description="Verify firewall is on",
                ),
                Op(
                    shell="/usr/libexec/ApplicationFirewall/socketfilterfw",
                    args=("--getstealthmode",),
                    description="Verify stealth mode is on",
                ),
            ],
            rollback_ops=[
                Op(
                    shell="/usr/libexec/ApplicationFirewall/socketfilterfw",
                    args=("--setglobalstate", "off"),
                    requires_sudo=True,
                    description="Disable firewall",
                ),
            ],
            tags=["firewall", "quickstart"],
        ),
        Action(
            id="quickstart.filevault.enable.02",
            chapter="21 · Quick-Start",
            chapter_num=21,
            title="Enable FileVault",
            risk=RiskLevel.DESTRUCTIVE,
            type=ActionType.MUTATE,
            description="Enable full-disk encryption via FileVault",
            ops=[
                Op(
                    shell="fdesetup",
                    args=("enable",),
                    requires_sudo=True,
                    description="Enable FileVault",
                ),
            ],
            verify_ops=[
                Op(shell="fdesetup", args=("status",), description="Verify FileVault is on"),
            ],
            rollback_ops=[],  # FileVault disable is complex
            tags=["filevault", "disk", "quickstart"],
            requires_reboot=True,
        ),
        Action(
            id="quickstart.browser.ublock.03",
            chapter="21 · Quick-Start",
            chapter_num=21,
            title="Install uBlock Origin (Firefox)",
            risk=RiskLevel.SAFE,
            type=ActionType.INSTALL,
            description="Open Firefox add-on page for uBlock Origin",
            ops=[
                Op(
                    shell="open",
                    args=("https://addons.mozilla.org/en-US/firefox/addon/ublock-origin/",),
                    description="Open uBlock Origin page",
                ),
            ],
            verify_ops=[],
            rollback_ops=[],
            tags=["browser", "quickstart"],
        ),
        Action(
            id="quickstart.hosts.blocklist.04",
            chapter="21 · Quick-Start",
            chapter_num=21,
            title="Block malware domains via /etc/hosts",
            risk=RiskLevel.SAFE,
            type=ActionType.MUTATE,
            description="Append StevenBlack blocklist to /etc/hosts",
            ops=[
                Op(
                    shell="curl",
                    args=("-L", "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts"),
                    capture=True,
                    description="Download blocklist",
                ),
                Op(
                    shell="tee",
                    args=("-a", "/etc/hosts"),
                    requires_sudo=True,
                    description="Append to hosts file",
                ),
            ],
            verify_ops=[
                Op(
                    shell="grep",
                    args=("StevenBlack", "/etc/hosts"),
                    description="Verify blocklist present",
                ),
            ],
            rollback_ops=[
                Op(
                    shell="sed",
                    args=("-i.bak", "/StevenBlack/d", "/etc/hosts"),
                    requires_sudo=True,
                    description="Remove StevenBlack entries",
                ),
            ],
            tags=["dns", "hosts", "quickstart"],
        ),
    ]


def _parse_chapter_body(chapter_num: int, chapter_title: str, body: str) -> list[Action]:
    """Extract actions from a single chapter's markdown body."""
    actions: list[Action] = []

    # Split by risk-level headers (**N · Title**)
    sections = _LEVEL_RE.split(body)
    # sections: [preamble, level, title, content, level, title, content, ...]

    for action_counter, j in enumerate(range(1, len(sections), 3), start=1):
        level = int(sections[j])
        level_title = sections[j + 1].strip()
        content = sections[j + 2] if j + 2 < len(sections) else ""

        risk = RiskLevel(level)
        action_id = f"{_slug(chapter_title)}.{_slug(level_title)}.{action_counter:02d}"

        ops = _extract_ops(content)
        verify_ops = _extract_ops(
            _extract_section(content, "verify") or _extract_section(content, "Expected") or ""
        )
        rollback_ops = _infer_rollback(ops)

        actions.append(
            Action(
                id=action_id,
                chapter=f"{chapter_num} · {chapter_title}",
                chapter_num=chapter_num,
                title=level_title,
                risk=risk,
                type=_infer_type(ops),
                description=_first_sentence(content) or level_title,
                ops=ops,
                verify_ops=verify_ops,
                rollback_ops=rollback_ops,
                tags=_infer_tags(chapter_title, level_title),
                requires_reboot=_needs_reboot(content),
            )
        )

    return actions


def _extract_ops(text: str) -> list[Op]:
    """Pull all bash code blocks and turn them into Ops."""
    ops: list[Op] = []
    for match in _CODE_RE.finditer(text):
        code = match.group(1).strip()
        for line in code.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # Heuristic: split into shell + args
            parts = line.split()
            shell = parts[0]
            args = tuple(parts[1:])
            requires_sudo = shell == "sudo"
            if requires_sudo and args:
                shell = args[0]
                args = args[1:]
            ops.append(
                Op(
                    shell=shell,
                    args=args,
                    requires_sudo=requires_sudo,
                    description=line,
                )
            )
    return ops


def _infer_type(ops: list[Op]) -> ActionType:
    if not ops:
        return ActionType.READ
    if any(o.shell in ("brew", "curl", "hdiutil", "cp", "open") for o in ops):
        return ActionType.INSTALL
    if any(o.requires_sudo for o in ops):
        return ActionType.MUTATE
    return ActionType.READ


def _infer_rollback(ops: list[Op]) -> list[Op]:
    """Best-effort inverse for common macOS commands."""
    rollback: list[Op] = []
    for op in ops:
        if op.shell == "defaults" and "write" in op.args:
            try:
                idx = op.args.index("write")
                domain = op.args[idx + 1]
                key = op.args[idx + 2]
                rollback.append(
                    Op(
                        shell="defaults",
                        args=("delete", domain, key),
                        description=f"Rollback: delete {domain} {key}",
                    )
                )
            except (ValueError, IndexError):
                pass
        elif op.shell == "launchctl" and "disable" in op.args:
            try:
                idx = op.args.index("disable")
                service = op.args[idx + 1]
                rollback.append(
                    Op(
                        shell="launchctl",
                        args=("enable", service),
                        description=f"Rollback: enable {service}",
                    )
                )
            except (ValueError, IndexError):
                pass
        elif op.shell == "pfctl" and "-e" in op.args:
            rollback.append(Op(shell="pfctl", args=("-d",), description="Rollback: disable pf"))
        elif op.shell == "socketfilterfw" and "--setglobalstate" in op.args and "on" in op.args:
            rollback.append(
                Op(
                    shell="socketfilterfw",
                    args=("--setglobalstate", "off"),
                    description="Rollback: disable firewall",
                )
            )
    return rollback


def _infer_tags(chapter_title: str, level_title: str) -> list[str]:
    tags = []
    text = f"{chapter_title} {level_title}".lower()
    tag_map = {
        "firewall": "firewall",
        "filevault": "disk",
        "lockdown": "lockdown",
        "dns": "dns",
        "hosts": "dns",
        "pf": "pf",
        "brew": "brew",
        "homebrew": "brew",
        "service": "services",
        "launchd": "services",
        "siri": "siri",
        "spotlight": "spotlight",
        "browser": "browser",
        "tor": "tor",
        "vpn": "vpn",
        "messenger": "messaging",
        "signal": "messaging",
        "malware": "malware",
        "gatekeeper": "gatekeeper",
        "sip": "sip",
        "password": "passwords",
        "backup": "backup",
        "wifi": "wifi",
        "ssh": "ssh",
        "monitor": "monitoring",
        "audit": "auditing",
        "ca": "certificates",
        "bluetooth": "bluetooth",
        "sharing": "sharing",
        "hardware": "hardware",
        "admin": "accounts",
    }
    for keyword, tag in tag_map.items():
        if keyword in text:
            tags.append(tag)
    return list(set(tags))


def _needs_reboot(content: str) -> bool:
    return any(kw in content.lower() for kw in ("restart", "reboot", "login again", "relog"))


# ---------------------------------------------------------------------------
# Cheat-sheet path resolution
# ---------------------------------------------------------------------------

_DEFAULT_CHEATSHEET = Path.home() / "MasterBase" / "privacy" / "MacOS-Privacy-CheatSheet.md"


def get_cheatsheet_path() -> Path:
    """Resolve the cheat-sheet path, preferring GHOSTY_CHEATSHEET env var."""
    env = os.environ.get("GHOSTY_CHEATSHEET")
    return Path(env) if env else _DEFAULT_CHEATSHEET
