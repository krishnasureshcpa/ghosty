"""
Phantom theme -- true-color-first palette with graceful 16/256-color fallback.

Design rules (per the project's CLI design quality bar):
    1. NEVER rainbow-vomit — 4 semantic hues only.
    2. Detect terminal capability, then pick the best palette automatically.
    3. `--no-color` and `NO_COLOR=1` must strip every ANSI code.
    4. Components are tiny, immutable, and side-effect free.

Palette
-------
    Phantom violet  #7C5CFF   — primary, accent, banner gradient start
    Wraith cyan     #22D3EE   — success, banner gradient end
    Ember amber     #FFC857   — warning, attention
    Crimp red       #FF5C7C   — danger, destructive confirm
    Slate grey      #94A3B8   — secondary text, metadata
    Obsidian        #0B0F1A   — panel background fill
    Bone            #F8FAFC   — primary text on dark surfaces

Pairs are designed against both dark and light terminal backgrounds by
running on a 24-bit channel mix tuned for AA contrast against `#FFFFFF`
and `#000000`.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from enum import StrEnum

from rich.color import Color
from rich.console import Console
from rich.theme import Theme as RichTheme

# ---------------------------------------------------------------------------
# Capability detection — single source of truth for color/style behaviour
# ---------------------------------------------------------------------------


class Capability(StrEnum):
    """What this terminal can render."""

    TRUECOLOR = "truecolor"  # 24-bit RGB
    ENHANCED = "256"  # 256-color palette
    BASIC = "16"  # ANSI 16 colors only
    PLAIN = "0"  # no color (NO_COLOR, dumb pipe, …)


def detect_capability(console: Console | None = None) -> Capability:
    """Return the highest color capability the runtime supports."""
    if os.environ.get("NO_COLOR"):
        return Capability.PLAIN

    c = console or Console()
    term = os.environ.get("TERM", "")
    colorterm = os.environ.get("COLORTERM", "")

    # Piped / non-tty always degrades
    if not c.is_terminal:
        return Capability.PLAIN

    # Honor CLI override
    if os.environ.get("PHANTOM_NO_COLOR") == "1":
        return Capability.PLAIN

    # Even dumb terminals get plain-mode treatment
    if term in ("dumb", ""):
        return Capability.PLAIN

    if "truecolor" in colorterm.lower() or "24bit" in colorterm.lower():
        return Capability.TRUECOLOR

    # Mac Terminal.app advertises "xterm-256color" but actually supports truecolor
    if sys.platform == "darwin" and "256color" in term:
        return Capability.TRUECOLOR

    if "256color" in term:
        return Capability.ENHANCED

    return Capability.BASIC


# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Palette:
    """A semantic color pack tied to one capability tier."""

    capability: Capability
    violet: str
    cyan: str
    amber: str
    crimp: str
    slate: str
    obsidian: str
    bone: str

    @classmethod
    def for_capability(cls, cap: Capability) -> Palette:
        if cap is Capability.TRUECOLOR:
            return cls(
                capability=cap,
                violet="#7C5CFF",
                cyan="#22D3EE",
                amber="#FFC857",
                crimp="#FF5C7C",
                slate="#94A3B8",
                obsidian="#0B0F1A",
                bone="#F8FAFC",
            )
        if cap is Capability.ENHANCED:
            # Same hues as 256 palette indices → still a clean look, less pop
            return cls(
                capability=cap,
                violet="\x1b[38;5;99m",  # 99 ~ #5f5fff violet
                cyan="\x1b[38;5;51m",  # 51 ~ #00ffff cyan
                amber="\x1b[38;5;221m",  # 221 ~ #ffd75f warm
                crimp="\x1b[38;5;204m",  # 204 ~ #ff5f87 coral
                slate="\x1b[38;5;245m",  # 245 ~ #8a8a8a
                obsidian="\x1b[48;5;236m",  # panel fill
                bone="\x1b[38;5;255m",
            )
        if cap is Capability.BASIC:
            return cls(
                capability=cap,
                violet="\x1b[35m",  # magenta
                cyan="\x1b[36m",  # cyan
                amber="\x1b[33m",  # yellow
                crimp="\x1b[31m",  # red
                slate="\x1b[37m",  # white
                obsidian="",  # no fills in 16-color
                bone="\x1b[37m",
            )
        # PLAIN
        return cls(
            capability=cap,
            violet="",
            cyan="",
            amber="",
            crimp="",
            slate="",
            obsidian="",
            bone="",
        )


def pick_palette(console: Console | None = None) -> Palette:
    return Palette.for_capability(detect_capability(console))


# ---------------------------------------------------------------------------
# Rich theme — fed into every Console we create
# ---------------------------------------------------------------------------


def rich_theme(p: Palette) -> RichTheme:
    """Build a Rich Theme mapping semantic names to our palette."""
    styled = {
        "phantom.violet": Color.parse(p.violet) if p.violet else "default",
        "phantom.cyan": Color.parse(p.cyan) if p.cyan else "default",
        "phantom.amber": Color.parse(p.amber) if p.amber else "default",
        "phantom.crimp": Color.parse(p.crimp) if p.crimp else "default",
        "phantom.slate": Color.parse(p.slate) if p.slate else "default",
        "phantom.bone": Color.parse(p.bone) if p.bone else "default",
        # Semantic aliases
        "title": "phantom.violet",
        "subtitle": "phantom.cyan",
        "info": "phantom.cyan",
        "success": "phantom.cyan",
        "warning": "phantom.amber",
        "danger": "phantom.crimp",
        "muted": "phantom.slate",
        "key": "phantom.amber bold",
        "badge": "phantom.violet on #1A1F2E",
    }
    return RichTheme(styled)  # type: ignore[arg-type]  # ponytail: dict[str, Color|str] is valid at runtime


def make_console(*, force_color: bool = False) -> Console:
    """Single canonical Console — used by splash, doctor JSON, etc."""
    force = force_color or os.environ.get("PHANTOM_COLOR") == "always"
    return Console(
        theme=rich_theme(pick_palette()),
        force_terminal=force,
        record=True,
        highlight=False,
        legacy_windows=False,
        soft_wrap=False,
    )


__all__ = [
    "Capability",
    "Palette",
    "detect_capability",
    "make_console",
    "pick_palette",
    "rich_theme",
]
