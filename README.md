<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/ghosty.gif">
    <img alt="Ghosty mascot" src="assets/ghosty.gif" width="280">
  </picture>
</p>

<h1 align="center">GHOSTY</h1>

<h3 align="center"><i>macOS Privacy & Security TUI</i></h3>

<p align="center">
  <a href="#install">Install</a> •
  <a href="#usage">Usage</a> •
  <a href="#tech">Tech</a> •
  <a href="#contributing">Contribute</a>
</p>

<p align="center">
  <img src="https://img.shields.io/github/actions/workflow/status/krishnasureshcpa/ghosty/ci.yml?style=flat&label=CI&labelColor=0D1117&color=1F6FEB" alt="CI">
  <img src="https://img.shields.io/badge/Python-3.12%2B-0D1117?style=flat&logo=python&logoColor=8B5CF6&labelColor=0D1117&color=8B5CF6" alt="Python">
  <img src="https://img.shields.io/badge/TUI-Textual-0D1117?style=flat&labelColor=0D1117&color=8B5CF6" alt="Textual">
  <img src="https://img.shields.io/badge/macOS-13%2B-0D1117?style=flat&logo=apple&logoColor=white&labelColor=0D1117&color=white" alt="macOS">
  <img src="https://img.shields.io/github/license/krishnasureshcpa/ghosty?style=flat&label=License&labelColor=0D1117&color=8B5CF6" alt="License">
</p>

---

**Ghosty** turns the 919-line *macOS Security & Privacy Guide* into a typed, reversible action catalog wrapped in a Textual TUI — sidebar navigation, live before/after diffs, parallel execution, dry-run by default, and one-command rollback.

20 chapters · 80+ reversible actions · Snapshot → Verify → Undo

---

## Install

**Pre-built (recommended)** — no clone needed, one command:

```bash
uv tool install ghosty-cli          # uv (fastest)
pipx install ghosty-cli             # pipx
brew install krishnasureshcpa/tap/ghosty  # Homebrew
```

**From source** — `ghosty` available globally after install:

```bash
git clone https://github.com/krishnasureshcpa/ghosty
cd ghosty
make install                        # one command → ghosty on PATH
# or: python install.py             # interactive installer
# or: uv tool install .             # same as make install
```

**Run from source** (no global install):

```bash
cd ghosty && uv sync && uv run ghosty
```

---

## Usage

```text
ghosty                  Launch the TUI
ghosty test             Self-test + welcome screen
ghosty doctor           System health dashboard
ghosty harden all       Non-interactive full hardening
ghosty harden firewall  Single chapter
ghosty snapshot save    Snapshot current state
ghosty rollback         Undo last action
ghosty --help           Full CLI reference
```

### Inside the TUI

| Key           | Action                               |
|---------------|--------------------------------------|
| `up/down`     | Navigate action list                 |
| `1-9`         | Jump to chapter                      |
| `space`       | Toggle selection                     |
| `enter`       | Inspect / execute                    |
| `d`           | Dry-run preview                      |
| `a`           | Apply (with confirmation)            |
| `u`           | Undo (last applied)                  |
| `/`           | Fuzzy search                         |
| `?`           | Help overlay                         |

---

## Features

| Area               | Detail                                                              |
|--------------------|---------------------------------------------------------------------|
| **Curated catalog** | Every action authored from the macOS privacy cheat sheet — nothing made up |
| **Snapshots**       | Every mutable action preceded by state capture, recorded in JSONL   |
| **Rollback**        | `ghosty undo` replays the inverse op-store in dependency order      |
| **Parallel grid**   | 4-action pipelines render at ~30 fps with ETA and per-cell status   |
| **Doctor**          | Checks Apple Silicon, SIP, FileVault, brew, sudo, network isolation |
| **Dry-run**         | Every command shows preview before sudo, with confirm/cancel        |
| **Real installs**   | brew install actually runs, binary verified, optionally launched    |
| **JSON output**     | `--json` flag for scripting and CI integration                      |
| **Overrideable**    | `$GHOSTY_CHEATSHEET` for a custom privacy guide path                |
| **macOS guard**     | CLI exits with clear error on unsupported platforms                 |

---

## Tech

| Layer     | Choice                                                                 |
|-----------|------------------------------------------------------------------------|
| Language  | Python 3.12+                                                          |
| TUI       | [Textual](https://textual.textualize.com) ≥ 0.85 (async, CSS, animations) |
| Styling   | [Rich](https://rich.readthedocs.io) ≥ 13 (gradients, syntax, progress)    |
| CLI       | [Click](https://click.palletsprojects.com) ≥ 8.1                          |
| Model     | [Pydantic](https://pydantic.dev) v2                                       |
| Shell     | `asyncio` — no races, no zombies                                          |
| Resolver  | `uv` — 10× faster than pip + venv                                         |

### Structure

```
src/ghosty/
├── app/          — Textual app shell, screens, keybindings
├── catalog/      — 20 chapters of curated hardening actions
├── runner/       — Execution engine, parallel grid, rollback
├── backends/     — macOS defaults, brew, file ops, launchctl
├── theme/        — Color palette, styling tokens
└── cli.py        — Click entrypoint
```

---

## v1 → v2

| v1 (Go + Bubble Tea, 6 items)     | v2 (Python + Textual, 20 chapters · 80+ actions) |
|-----------------------------------|---------------------------------------------------|
| Install buttons were stubs        | Every click actually runs brew / defaults write   |
| Manual, single-step               | Snapshot → mutate → verify → undo workflow       |
| No rollback                       | Every action records its inverse                  |
| Static screenshot                 | Animated banner, keyframed transitions, live grid |
| Plain `main.go`                   | Modular `src/ghosty/` with 6 packages             |

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Catalog additions start as PRs against
`catalog/` with a verification op proving the setting changed.

Report vulnerabilities per [SECURITY.md](SECURITY.md) — not as public issues.

---

## License

MIT © 2026 Krishna Suresh CPA.

---

## Acknowledgments

- [Textualize](https://textual.textualize.com) — Textual, Rich, and the terminal renaissance
- [drduh/macOS-Security-and-Privacy-Guide](https://github.com/drduh/macOS-Security-and-Privacy-Guide) — the canonical hardening source
- The macOS security community

<p align="center">
  <a href="https://github.com/krishnasureshcpa/ghosty">★ Star on GitHub</a>
</p>
