# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] — 2026-06-27

### Added
- Complete Python + Textual TUI replacement of the v1 Go/Bubble Tea prototype
- 20 chapters of macOS privacy and security hardening guidance (80+ actions)
- Curated action catalog from the macOS Privacy & Security Guide (drduh)
- 6 interactive TUI screens: Home, Catalog, Detail, Run, Doctor, Replay
- 4 TUI widgets: StatusBar, ProgressGrid, ActionProgressCell, ActionCard
- Snapshot → mutate → verify → undo workflow engine
- Automatic snapshots before every mutable action (JSONL store at `~/.config/phantom/store`)
- First-class rollback (`phantom undo`, dependency-ordered inverse replay)
- Live parallel execution grid (~30 fps, per-cell ETA and log tails)
- Doctor mode — checks SIP, Apple Silicon, FileVault, secure boot, brew, sudo, network
- Dry-run by default with explicit preview and confirmation
- `--json` output flag for scripting and CI integration
- Apple-grade TUI palette (`#7C5CFF` violet, `#22D3EE` cyan, `#FFC857` amber)
- Gradient figlet banner, animated status pills, keyframed transitions
- Click-based CLI with two entry points (`phantom` primary, `ghost` alias)
- Pydantic v2 models for catalog entries, actions, and execution state
- Async subprocess management via `asyncio` + `sh` library
- `uv`-based project management (uv.lock, uv.toml)

### Changed
- Complete architecture rewrite from Go → Python
- Project renamed to `phantom` with `ghosty` retained as legacy alias
- Action catalog expanded from 6 → 80+ items across 20 chapters
- Installation buttons replaced with actual `brew install` / `defaults write` execution

### Removed
- Go Bubble Tea prototype (v1)
- Placeholder install buttons
- Static screenshot-of-UI demo approach

### Fixed
- No more single-step manual hardening — full snapshot → verify → undo lifecycle
- Proper terminal capability detection (`NO_COLOR`, `TERM=dumb`, CJK widths)
- Zombie-free subprocess management

[2.0.0]: https://github.com/krishnasureshcpa/ghosty/releases/tag/v2.0.0
