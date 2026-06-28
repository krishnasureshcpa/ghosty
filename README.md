# Phantom — macOS Privacy & Security TUI

> **Version 2 · Built from the ground up**
> Apple-grade privacy hardening, audit, and tool installation — driven from a single keyboard-first terminal app, across 20 chapters of curated hardening guidance.

[![CI](https://img.shields.io/badge/CI-GitHub_Actions-blue)](https://github.com/krishnasureshcpa/ghosty/actions)
[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB)](https://www.python.org)
[![Textual](https://img.shields.io/badge/TUI-Textual-7C5CFF)](https://textual.textualize.com)
[![Rich](https://img.shields.io/badge/Rich-13%2B-22D3EE)](https://rich.readthedocs.io)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![macOS](https://img.shields.io/badge/macOS-13%2B-black)](https://www.apple.com/macos)
[![Apple Silicon](https://img.shields.io/badge/Apple%20Silicon-arm64-black)](https://support.apple.com/en-us/HT211814)

**Phantom** (CLI command: `phantom`) takes the 919-line **macOS Privacy & Security
Guide**, transforms it into a typed, reversible action catalog, and wraps it in a
Textual TUI with sidebar navigation, live before/after diffs, parallel execution,
dry-run by default, and one-line rollback.

```text
┌─ Home ──────────────────────────────┐ ┌─ Catalog ──────────────────────────┐
│ ░░░░░░░░██░░░░░░░░░░░░░░░░░░░░░░░░░░ │ │ 🛡  Firewall                          │
│ ░ P H A N T O M · 𝓬𝓵𝓲 · 𝚟2 ░░░░░░░░ │ │ 🔒  FileVault & firmware             │
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │ │ 🥷  Lockdown Mode                    │
└─────────────────────────────────────┘ │ 📡  DNS · hosts · pf                │
                                        │ 📦  Homebrew hygiene                │
  Phantom works against:                  │ 🌐  Browser, Tor, VPN               │
  · 20 chapters of macOS hardening        │ 💬  Messengers, E2EE                │
  · 80+ atomic, reversible actions        │ ⚙️   Services, Siri, Spotlight       │
  · Snapshot → mutate → verify → undo     │ 🩺  Doctor · Snapshot · Replay       │
                                          └─────────────────────────────────────┘
```

---

## What's different from v1

| v1 (rejected)              | v2                                                                       |
|---------------------------|--------------------------------------------------------------------------|
| Go + Bubble Tea, 6 items  | Python + Textual, **20 chapters · 80+ actions**                          |
| Install buttons were stubs| **Every menu click actually runs** `brew install` / `defaults write` etc.|
| Manual, single-step       | **Snapshot → mutate → verify → undo** workflow baked in                  |
| No rollback               | Every reversible action records its inverse in `~/.config/phantom/store` |
| Static screenshot of UI   | Animated gradient banner, keyframed transitions, live parallel grid      |
| Plain `main.go`           | Modular `src/phantom/{theme,catalog,runner,backends,app}`                |

---

## ✨ Features

- **🛡 Curated catalog** — every action was authored from the macOS privacy cheat sheet (Section 6.1–22). Nothing made up.
- **🎨 Apple-grade TUI** — Phantom palette (`#7C5CFF` violet, `#22D3EE` cyan, `#FFC857` amber), 4-level semantic colors, gradient figlet title, animated status pills.
- **📸 Automatic snapshots** — every mutable action is preceded by `snapshot.read()` and recorded in JSONL.
- **↺ First-class rollback** — `phantom undo` replays the inverse op-store, in dependency order.
- **🪟 Live parallel grid** — 4-action pipelines render at ~30 fps with ETA, per-cell status, and log tails.
- **🩺 Doctor mode** — checks Apple Silicon, SIP, firmware secure boot, FileVault, brew, sudo, Network isolation.
- **🧪 Dry-run by default** — every command renders an explicit preview before sudo, with `[Tab] confirm · [Esc] cancel`.
- **🤖 Real installs** — `brew install` actually runs, the resulting binary path is verified, and (optional) launched.
- **─JSON output** — `--json` flag for scripting & replay.
- **♿ Free of anti-patterns** — handles `NO_COLOR`, `TERM=dumb`, broken pipes, ghost cursors, CJK widths.

---

## 📦 Install

```bash
brew install krishnasureshcpa/tap/phantom      # Homebrew (recommended)

# or
uv tool install phantom-cli

# or
git clone https://github.com/krishnasureshcpa/ghosty
cd ghosty
uv sync
uv run phantom
```

> The old `ghosty` binary was a placeholder. **Phantom v2 is published under the
> name `phantom`** — `ghost` retained as a compatibility alias.

---

## ⌨️ Usage

```text
phantom                       Launch the TUI
phantom harden firewall       Non-interactive harden flow
phantom harden all --json     Audit-friendly JSON output
phantom doctor                System health dashboard
phantom snapshot save         Snapshot current state
phantom rollback              Replay inverse op-store
phantom replay                List executed actions, optional re-run
phantom install lulu          One-shot install w/ verification
phantom undo <id>             Undo the action with ID
phantom --help                Full CLI surface
```

Inside the TUI:

| Key       | Action                                  |
|-----------|-----------------------------------------|
| `↑/↓`     | Navigate action list                    |
| `1-9`     | Jump to chapter                         |
| `space`   | Toggle selection                        |
| `enter`   | Inspect / execute selected              |
| `d`       | Dry-run preview (default for mutates)   |
| `a`       | Apply (with confirmation prompt)        |
| `u`       | Undo (last applied)                     |
| `/`       | Fuzzy search across catalog             |
| `?`       | Help overlay                            |
| `q`       | Quit (only from home)                   |

---

## 🧰 Tech

- **Language:** Python 3.12+
- **TUI:** [Textual](https://textual.textualize.com) ≥ 0.85 (async, animations, CSS)
- **Styles:** [Rich](https://rich.readthedocs.io) ≥ 13 (gradient, syntax, progress)
- **CLI:** [Click](https://click.palletsprojects.com) ≥ 8.1
- **Validation:** [Pydantic](https://pydantic.dev) v2
- **Async shell:** `asyncio` + `sh` (no race conditions, no zombies)
- **Resolver:** `uv` (10× faster than pip+venv)

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). All contributors agree to the
[Code of Conduct](CODE_OF_CONDUCT.md). Catalog additions begin as PRs against
`catalog/` and require a verification op that proves the setting changed.

---

## 🔐 Security

Report vulnerabilities per [SECURITY.md](SECURITY.md) — please don't file them
as public issues. Phantom itself requires sudo only for the specific operations
that need it; everything else runs unprivileged.

---

## 📝 License

[MIT](LICENSE) © 2026 Krishna Suresh CPA.

---

## 🙏 Acknowledgements

- [Textualize](https://textual.textualize.com) — for Textual, Rich, and the entire terminal-app renaissance.
- [drduh/macOS-Security-and-Privacy-Guide](https://github.com/drduh/macOS-Security-and-Privacy-Guide) — the canonical source of all hardening guidance.
- [Hexidine privacy cheatsheet](~/MasterBase/privacy/MacOS-Privacy-CheatSheet.md) — the working catalog mirror.
- [phmullins/awesome-macos-commandline](https://github.com/phmullins/awesome-macos-commandline) — for the curated tool index.

---

<p align="center">Built with 🛠️ for Apple Silicon · ⭐ <a href="https://github.com/krishnasureshcpa/ghosty">Star on GitHub</a></p>
