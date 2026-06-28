<picture>
  <source media="(prefers-color-scheme: dark)" srcset="logo/ghosty.svg">
  <img alt="Ghosty" src="logo/ghosty.svg" width="120" align="right">
</picture>

# Ghosty — macOS Privacy & Security TUI

> **v2.0.1 — Consumer-ready release**  
> Apple-grade privacy hardening, audit, and tool installation — driven from a single keyboard-first terminal app, across 20 chapters of curated hardening guidance.

[![CI](https://github.com/krishnasureshcpa/ghosty/actions/workflows/ci.yml/badge.svg)](https://github.com/krishnasureshcpa/ghosty/actions)
[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![Textual](https://img.shields.io/badge/TUI-Textual-7C5CFF?logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMTIgMkwyIDdMMTIgMTJMMjIgN0wxMiAyWiIgZmlsbD0iIzdDNUNGRiIvPjxwYXRoIGQ9Ik0yIDdMMTIgMTJMMjIgN1YxM0wxMiAxOEwyIDEzVjdaIiBmaWxsPSIjN0M1Q0ZGIi8+PC9zdmc+&label=TUI)](https://textual.textualize.com)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![macOS](https://img.shields.io/badge/macOS-13%2B-black?logo=apple&logoColor=white)](https://www.apple.com/macos)
[![Stars](https://img.shields.io/github/stars/krishnasureshcpa/ghosty?style=flat&logo=github)](https://github.com/krishnasureshcpa/ghosty)

**Ghosty** (CLI: `ghosty`, alt: `ghost` / `gho`) takes the 919-line **macOS
Privacy & Security Guide**, transforms it into a typed, reversible action
catalog, and wraps it in a Textual TUI with sidebar navigation, live
before/after diffs, parallel execution, dry-run by default, and one-line
rollback.

```text
+-- Home -----------------------------+ +-- Catalog -------------------------+
|                                      | | Firewall                           |
|   G H O S T Y  .  c l i  .  v2     | | FileVault & firmware              |
|                                      | | Lockdown Mode                     |
+--------------------------------------+ | DNS . hosts . pf                 |
                                          | Homebrew hygiene                 |
  Ghosty works against:                   | Browser, Tor, VPN                |
  . 20 chapters of macOS hardening        | Messengers, E2EE                 |
  . 80+ atomic, reversible actions        | Services, Siri, Spotlight        |
  . Snapshot -> mutate -> verify -> undo  | Doctor . Snapshot . Replay        |
                                          +-----------------------------------+
```

---

## Install

```bash
# Homebrew (recommended)
brew install krishnasureshcpa/tap/ghosty

# pipx / uv tool
uv tool install ghosty-cli
pipx install ghosty-cli

# git clone
git clone https://github.com/krishnasureshcpa/ghosty
cd ghosty
uv sync
uv run ghosty

# SSH
git clone git@github.com:krishnasureshcpa/ghosty.git

# gh CLI
gh repo clone krishnasureshcpa/ghosty
```

---

## Usage

```text
ghosty                        Launch the TUI
ghost                         Same as ghosty (shorter alias)
gho                           Shortest alias
ghosty doctor                 System health dashboard
ghosty harden all             Non-interactive full hardening
ghosty harden firewall        Single chapter
ghosty harden all --json      Audit-friendly JSON output
ghosty snapshot save          Snapshot current state
ghosty rollback               Undo last action
ghosty replay                 Execution history
ghosty install lulu           One-shot brew install + verify
ghosty undo <id>              Undo specific action by ID
ghosty --help                 Full CLI reference
```

Inside the TUI:

| Key     | Action                                |
|---------|---------------------------------------|
| `up/down` | Navigate action list                |
| `1-9`   | Jump to chapter                       |
| `space` | Toggle selection                      |
| `enter` | Inspect / execute selected            |
| `d`     | Dry-run preview                       |
| `a`     | Apply (with confirmation prompt)      |
| `u`     | Undo (last applied)                   |
| `/`     | Fuzzy search across catalog           |
| `?`     | Help overlay                          |
| `q`     | Quit (only from home)                 |

---

## What's different from v1

| v1 (rejected)               | v2                                                               |
|-----------------------------|------------------------------------------------------------------|
| Go + Bubble Tea, 6 items    | Python + Textual, **20 chapters . 80+ actions**                  |
| Install buttons were stubs  | **Every menu click actually runs** brew/defaults write etc.      |
| Manual, single-step         | **Snapshot -> mutate -> verify -> undo** workflow baked in       |
| No rollback                 | Every reversible action records its inverse in `~/.config/ghosty/store` |
| Static screenshot of UI     | Animated gradient banner, keyframed transitions, live grid       |
| Plain `main.go`             | Modular `src/ghosty/{theme,catalog,runner,backends,app}`         |

---

## Features

| Icon | Feature                                        |
|------|------------------------------------------------|
| <img src="https://raw.githubusercontent.com/feathericons/feather/master/icons/shield.svg" width="18"> | **Curated catalog** -- every action authored from the macOS privacy cheat sheet. Nothing made up. |
| <img src="https://raw.githubusercontent.com/feathericons/feather/master/icons/palette.svg" width="18"> | **Apple-grade TUI** -- Ghosty palette (`#7C5CFF` violet, `#22D3EE` cyan, `#FFC857` amber), 4-level semantic colors, gradient title, animated status pills. |
| <img src="https://raw.githubusercontent.com/feathericons/feather/master/icons/camera.svg" width="18"> | **Automatic snapshots** -- every mutable action is preceded by state capture and recorded in JSONL. |
| <img src="https://raw.githubusercontent.com/feathericons/feather/master/icons/rotate-ccw.svg" width="18"> | **First-class rollback** -- `ghosty undo` replays the inverse op-store in dependency order. |
| <img src="https://raw.githubusercontent.com/feathericons/feather/master/icons/grid.svg" width="18"> | **Live parallel grid** -- 4-action pipelines render at ~30 fps with ETA, per-cell status, and log tails. |
| <img src="https://raw.githubusercontent.com/feathericons/feather/master/icons/activity.svg" width="18"> | **Doctor mode** -- checks Apple Silicon, SIP, FileVault, brew, sudo, network isolation. |
| <img src="https://raw.githubusercontent.com/feathericons/feather/master/icons/eye.svg" width="18"> | **Dry-run by default** -- every command renders an explicit preview before sudo, with confirm/cancel. |
| <img src="https://raw.githubusercontent.com/feathericons/feather/master/icons/terminal.svg" width="18"> | **Real installs** -- `brew install` actually runs, binary path verified, optionally launched. |
| <img src="https://raw.githubusercontent.com/feathericons/feather/master/icons/code.svg" width="18"> | **--JSON output** -- `--json` flag for scripting and CI integration. |
| <img src="https://raw.githubusercontent.com/feathericons/feather/master/icons/check-circle.svg" width="18"> | **Free of anti-patterns** -- handles `NO_COLOR`, `TERM=dumb`, broken pipes, ghost cursors, CJK widths. |
| <img src="https://raw.githubusercontent.com/feathericons/feather/master/icons/settings.svg" width="18"> | **Overrideable cheatsheet path** -- set `$GHOSTY_CHEATSHEET` for a custom privacy guide; defaults to `~/.config/ghosty/cheatsheet.md`. |
| <img src="https://raw.githubusercontent.com/feathericons/feather/master/icons/slash.svg" width="18"> | **macOS-only guard** -- CLI exits with a clear error on unsupported platforms. |

---

## Tech

- **Language:** Python 3.12+
- **TUI:** [Textual](https://textual.textualize.com) >= 0.85 (async, animations, CSS)
- **Styles:** [Rich](https://rich.readthedocs.io) >= 13 (gradient, syntax, progress)
- **CLI:** [Click](https://click.palletsprojects.com) >= 8.1
- **Validation:** [Pydantic](https://pydantic.dev) v2
- **Async shell:** `asyncio` (no race conditions, no zombies)
- **Resolver:** `uv` (10x faster than pip+venv)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). All contributors agree to the
[Code of Conduct](CODE_OF_CONDUCT.md). Catalog additions begin as PRs against
`catalog/` and require a verification op that proves the setting changed.

---

## Security

Report vulnerabilities per [SECURITY.md](SECURITY.md) -- please don't file them
as public issues. Ghosty itself requires sudo only for the specific operations
that need it; everything else runs unprivileged.

---

## License

[MIT](LICENSE) (c) 2026 Krishna Suresh CPA.

---

## Acknowledgements

- [Textualize](https://textual.textualize.com) -- for Textual, Rich, and the entire terminal-app renaissance.
- [drduh/macOS-Security-and-Privacy-Guide](https://github.com/drduh/macOS-Security-and-Privacy-Guide) -- the canonical source of all hardening guidance.
- [Hexidine privacy cheatsheet](https://github.com/drduh/macOS-Security-and-Privacy-Guide) -- the working catalog mirror (path overridable via `$GHOSTY_CHEATSHEET`).
- [Feather Icons](https://feathericons.com) -- clean SVG icons throughout this README.

---

<p align="center">Built with <img src="https://raw.githubusercontent.com/feathericons/feather/master/icons/tool.svg" width="16"> for Apple Silicon . <img src="https://raw.githubusercontent.com/feathericons/feather/master/icons/star.svg" width="16"> <a href="https://github.com/krishnasureshcpa/ghosty">Star on GitHub</a></p>
