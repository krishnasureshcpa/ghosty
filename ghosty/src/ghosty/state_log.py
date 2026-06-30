"""
Historical state log — ring buffer tracking the last N state transitions.
Enables undo/audit and replay of the TUI's state timeline.
(14-step loop requirement #12: Historical State Log)
"""

from __future__ import annotations

import time
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any

from ghosty.dispatcher import Msg, MsgX

_MAX_ENTRIES = 50


@dataclass(slots=True)
class LogEntry:
    """A single state transition record."""

    timestamp: float  # time.monotonic_ns // 1_000_000
    msg: Msg
    new_mode: str  # AppMode value
    summary: str = ""


@dataclass(slots=True)
class StateLog:
    """Fixed-cap ring buffer of state transitions."""

    _entries: list[LogEntry] = field(default_factory=list)
    _cursor: int = 0  # next write index

    def push(self, msg: Msg, new_mode: str, summary: str = "") -> None:
        """Append one log entry, evicting the oldest when at capacity."""
        entry = LogEntry(
            timestamp=time.monotonic_ns() // 1_000_000,
            msg=msg,
            new_mode=new_mode,
            summary=summary or msg.type.name,
        )

        if len(self._entries) < _MAX_ENTRIES:
            self._entries.append(entry)
        else:
            self._entries[self._cursor] = entry

        self._cursor = (self._cursor + 1) % _MAX_ENTRIES

    def recent(self, n: int = 10) -> list[LogEntry]:
        """Return the last *n* entries in chronological order."""
        if not self._entries:
            return []
        return self._entries[-n:]

    def all(self) -> list[LogEntry]:
        """Return all entries (oldest first)."""
        return list(self._entries)

    def filter_by(self, kind: MsgX) -> list[LogEntry]:
        """Return all entries matching a message type."""
        return [e for e in self._entries if e.msg.type == kind]

    def clear(self) -> None:
        self._entries.clear()
        self._cursor = 0

    def __len__(self) -> int:
        return len(self._entries)

    def __iter__(self) -> Iterator[LogEntry]:
        return iter(self._entries)
