# Ghosty — Complete Resource Index

> Curated reference for AI agents working on macOS privacy, terminal UIs, and premium GitHub branding.  
> Last updated: 2026-06-28

---

## 1. ANIMATION & IMMERSIVE TUI

| Priority | Resource | Why |
|----------|----------|-----|
| ★★★ | [Textual Animation Guide](https://textual.textualize.com/guide/animations/) | Official docs for CSS keyframes, transitions, easing — built into Ghosty's stack |
| ★★★ | [Rich Live Display](https://rich.readthedocs.io/en/stable/live.html) | Real-time updating terminal output (progress bars, status panels, spinners) |
| ★★★ | [Textual CSS Properties — animate](https://textual.textualize.com/guide/CSS/#animation) | `animate: name duration easing delay iteration-count;` — declarative keyframe animations in TUI |
| ★★ | [Bubble Tea Animations](https://github.com/charmbracelet/bubbletea) | Go-based TUI with frame-based animation (Ghosty v1 used this) |
| ★★ | [Gum — Terminal animations](https://github.com/charmbracelet/gum) | Shell-level animated components: spinners, progress bars, styled prompts |
| ★★ | [Textual Screens & Transitions](https://textual.textualize.com/guide/screens/#screen-transitions) | Slide/fade/zoom between screens — makes the TUI feel like a native app |
| ★ | [Terminal ASCII Animations](https://github.com/asciimoo/drawille) | Pixel-art in terminal using braille characters — for custom splash animations |
| ★ | [Textual Loading Indicator](https://textual.textualize.com/widgets/loading_indicator/) | Built-in spinner widget for async operations |

### Latest animation patterns (2025–2026):

| Pattern | What it does | Source |
|---------|-------------|--------|
| **CSS keyframes in TUI** | Declare `@keyframes float { 0% { opacity: 1; } 100% { opacity: 0.8; } }` right in Textual CSS | [Textual CSS Animations](https://textual.textualize.com/guide/animations/#keyframes) |
| **Rich `Progress` + `SpinnerColumn`** | Async progress bars with ETA, percentage, and animated spinner glyphs | [Rich Progress](https://rich.readthedocs.io/en/stable/progress.html) |
| **Textual `AutoMappedScreen`** | Auto-animated screen transitions with zero boilerplate | Textual 1.0+ |
| **Textual reactive attributes + `animate()`** | `self.my_widget.styles.opacity = 0.5` with auto-transition via `self.animate('my_prop', 42)` | [Textual Reactive](https://textual.textualize.com/guide/reactive/) |
| **Charm VHS** | Record terminal GIFs for READMEs — `vhs record` → `.gif` | [Charm VHS](https://github.com/charmbracelet/vhs) |

---

## 2. macOS PRIVACY & HARDENING (Core Domain)

| Resource | What It Covers |
|----------|----------------|
| [drduh/macOS-Security-and-Privacy-Guide](https://github.com/drduh/macOS-Security-and-Privacy-Guide) | **The canonical source** — 919-line guide covering firewall, FileVault, lockdown, DNS, Spotlight, brew, TOR, messengers, E2EE, and 20+ more chapters |
| [Apple Platform Security Guide](https://support.apple.com/guide/security/welcome/web) | Apple's official security documentation — SIP, SEP, Secure Boot, XProtect, Gatekeeper |
| [macOS Security Compliance Project](https://github.com/usnistgov/macos_security) | NIST macOS security benchmarks — CIS-level hardening profiles in YAML |
| [Objective-See Tools](https://objective-see.com/products.html) | Free macOS security tools: BlockBlock, ReiKey, KnockKnock, Lulu, RansomWhere? |
| [Lulu](https://github.com/objective-see/LuLu) | Open-source macOS firewall — Ghosty can auto-install via `brew` |
| [Homebrew Security Audit](https://github.com/Homebrew/homebrew-security) | Brew audit for known-vulnerable formulae |
| [Apple System Integrity Protection Guide](https://support.apple.com/en-us/HT204899) | SIP reference — csrutil status, configuration profiles |
| [macOS Launchd Reference](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html) | LaunchDaemons and LaunchAgents — used by Ghosty's `backends/launchctl` module |

---

## 3. GITHUB REPO BRANDING & PREMIUM README

| Resource | Why |
|----------|-----|
| [GitHub README Stats](https://github.com/anuraghazra/github-readme-stats) | Dynamic stats cards (stars, commits, languages) — embeddable in README |
| [Shields.io Badges](https://shields.io) | Custom SVG badges — Ghosty uses `style=flat&labelColor=0D1117&color=8B5CF6` for dark-mode native look |
| [GitHub Profile README Generator](https://github.com/rahuldkjain/github-profile-readme-generator) | Reference for premium README layouts, alignment, responsive `<picture>` tags |
| [GitHub Social Preview](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/customizing-your-repositorys-social-media-preview) | How to set the 1280×640px social preview card (shows up on link shares) |
| [GitHub Release Notes](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository) | Auto-generate release notes from tags + commits |
| [Prettier README Patterns](https://github.com/Louis3797/awesome-readme-template) | Collection of premium README templates |
| [GitHub Topics](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/classifying-your-repository-with-topics) | Add topics like `privacy`, `macOS`, `security`, `tui` for discoverability |
| [SVG Preview Optimization](https://developer.mozilla.org/en-US/docs/Web/SVG) | MDN SVG guide — Ghosty's logo is pure SVG for crisp rendering at any size |
| [Animated GIF in README](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/attaching-files) | GitHub supports `<img>` tags pointing to animated GIFs in the repo itself |

---

## 4. CLI TOOL DEVELOPMENT (Stack)

| Layer | Resource | What It Does |
|-------|----------|-------------|
| **TUI Framework** | [Textual](https://textual.textualize.com) | Async Python TUI with CSS styling, reactive widgets, animations. Ghosty's entire UI. |
| **Terminal Styling** | [Rich](https://rich.readthedocs.io) | Terminal markup, tables, progress bars, syntax highlighting, live display |
| **CLI Parser** | [Click](https://click.palletsprojects.com) | Subcommands, options, help auto-generation |
| **Config Models** | [Pydantic v2](https://docs.pydantic.dev/latest/) | Typed, validated configs with JSON schema export |
| **Async Shell** | [asyncio.create_subprocess_exec](https://docs.python.org/3/library/asyncio-subprocess.html) | Non-blocking shell execution — no zombies, no races |
| **Python Resolver** | [uv](https://docs.astral.sh/uv/) | 10× faster pip replacement. Used for install, sync, tool install |

### CLI polish / DX:

| Resource | Why |
|----------|-----|
| [NO_COLOR Standard](https://no-color.org) | Every CLI must respect this env var |
| [CLI Guidelines by clig.dev](https://clig.dev) | Canonical CLI UX guidelines — exit codes, stderr, `--json`, `--help` patterns |
| [Terminal Colors Reference](https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797) | Complete ANSI escape codes reference |
| [ASCII Art Archive](https://www.asciiart.eu) | Large ASCII art collection for splash banners |
| [Python `rich.inspect`](https://rich.readthedocs.io/en/stable/reference/inspect.html) | Instant object introspection for debug output |

---

## 5. MACOS-SPECIFIC TOOLS & COMMANDS

| Tool | What Ghosty Uses It For |
|------|------------------------|
| `defaults` | Read/write macOS user defaults (the bulk of hardening actions) |
| `plutil` | Property list manipulation |
| `csrutil status` | Check SIP (System Integrity Protection) state |
| `fdesetup status` | Check FileVault encryption status |
| `sysctl` | Kernel parameter inspection (`sysctl hw.optional.arm64`) |
| `pmset` | Power management settings |
| `spctl` | Gatekeeper assessment policy |
| `nvram` | Firmware settings (boot args, recovery) |
| `launchctl` | Manage launchd services (disable/enable Spotlight, Siri, etc.) |
| `networksetup` | Network configuration (DNS, proxy, firewall) |
| `scutil` | System configuration query |
| `brew` | Package manager — install/verify/uninstall security tools |
| [`mas`](https://github.com/mas-cli/mas) | Mac App Store CLI (for updating Apple apps) |
| [`machelper`](https://github.com/nickstenning/machelper) | Grant/revoke macOS permissions via CLI |

---

## 6. AI AGENT / DEVELOPER TOOLING REFERENCES

| Tool | Why It Matters |
|------|----------------|
| [Pydantic AI](https://ai.pydantic.dev) | Structured LLM output — if Ghosty ever gets AI-assisted actions |
| [OpenCode](https://github.com/opencode-ai/opencode) | The agent framework this session runs on |
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code) | Anthropic's terminal-based AI coding agent |
| [GitHub CLI `gh`](https://cli.github.com/manual/) | Full GitHub API from terminal — PRs, issues, releases |
| [LiveReview (`lrc`)](https://github.com/opencode-ai/lrc) | Pre-commit code review tool — currently enabled on this repo |
| [Ruff](https://docs.astral.sh/ruff/) | Python linter + formatter (used in CI + pre-commit) |
| [Mypy](https://mypy-lang.org) | Static typing for Python (strict mode in pyproject.toml) |
| [Pytest](https://docs.pytest.org) | Test framework with `pytest-asyncio` for async tests |
| [Freezegun](https://github.com/spulec/freezegun) | Mock `datetime.now()` in tests |

---

## 7. DESIGN & COLOR REFERENCES

| Resource | What It Provides |
|----------|-----------------|
| [Tailwind CSS Color Palette](https://tailwindcss.com/docs/customizing-colors) | Source of Ghosty's `#8B5CF6` violet (violet-500) |
| [Coolors Palette Generator](https://coolors.co) | Generate cohesive color schemes |
| [Realtime Colors](https://realtimecolors.com) | Live preview of color palettes on actual UI layouts |
| [SVG Backgrounds](https://www.svgbackgrounds.com) | Free SVG background patterns for README banners |
| [Font Awesome](https://fontawesome.com) | Icon font for CLI output (Ghosty uses minimal glyphs instead) |
| [Simple Icons](https://simpleicons.org) | Brand icons for shields.io badges — Python, macOS, GitHub |
| [Feather Icons](https://feathericons.com) | Clean open-source SVG icons — used in earlier README versions |
| [Nerd Fonts](https://www.nerdfonts.com) | Developer-focused patched fonts with powerline + icon glyphs |
| [SF Mono / JetBrains Mono](https://www.jetbrains.com/lp/mono/) | Monospace fonts used in Ghosty's SVG for terminal-style eye glyphs |

---

## 8. TEXTUAL ADVANCED PATTERNS

| Pattern | Link | What It Unlocks |
|---------|------|-----------------|
| **CSS Keyframes** | [Textual Animations](https://textual.textualize.com/guide/animations/) | Declarative `@keyframes` in TUI CSS |
| **Reactive Attributes** | [Textual Reactive](https://textual.textualize.com/guide/reactive/) | Auto-updating UI state with `reactive` descriptors |
| **Workers** | [Textual Workers](https://textual.textualize.com/guide/workers/) | Background thread/task management without blocking UI |
| **DataTable** | [Textual DataTable](https://textual.textualize.com/widgets/data_table/) | Sortable, styleable tables — Ghosty uses this for action catalogs |
| **Tree** | [Textual Tree](https://textual.textualize.com/widgets/tree/) | Hierarchical navigation — Ghosty uses for sidebar |
| **Tabs** | [Textual Tabs](https://textual.textualize.com/widgets/tabs/) | Tabbed interfaces |
| **Rich Log** | [Textual Log](https://textual.textualize.com/widgets/log/) | Real-time log viewer widget |
| **Auto-discovered Screens** | [Textual Screens](https://textual.textualize.com/guide/screens/) | Modal, full-screen, and popup screen management |

---

## 9. PRODUCTION CHECKS & CI/CD

| Resource | What It Covers |
|----------|---------------|
| [GitHub Actions workflow](https://docs.github.com/en/actions) | CI — lint, type-check, test on push/PR |
| [Coverage.py](https://coverage.readthedocs.io) | Test coverage measurement (configured in pyproject.toml) |
| [Semantic Versioning](https://semver.org) | Ghosty follows `MAJOR.MINOR.PATCH` |
| [Keep a Changelog](https://keepachangelog.com) | CHANGELOG format (Added, Changed, Fixed, Removed) |
| [Conventional Commits](https://www.conventionalcommits.org) | Commit message format: `type(scope): description` |
| [MIT License](https://opensource.org/licenses/MIT) | Ghosty's license — permissive, attribution-only |

---

## 10. PACKAGING & DISTRIBUTION

| Resource | What It Does |
|----------|-------------|
| [PyPI](https://pypi.org/project/ghosty-cli/) | Python package index — `pip install ghosty-cli` |
| [Homebrew Tap](https://github.com/krishnasureshcpa/homebrew-tap) | Homebrew formula — `brew install krishnasureshcpa/tap/ghosty` |
| [Hatchling](https://hatch.pypa.io/latest/) | Build backend — configured in pyproject.toml |
| [uv tool install](https://docs.astral.sh/uv/concepts/tools/) | One-command install: `uv tool install ghosty-cli` |
| [pipx](https://pypa.github.io/pipx/) | Isolated Python app installer |

---

## AI Agent Quick-Start Guide

If an AI agent lands here and needs to understand Ghosty:

```
1. README.md              → What the project is, how to install/use
2. CONTRIBUTING.md        → How to add catalog actions, PR workflow
3. ARCHITECTURE.md        → (if exists) Module structure, data flow
4. src/ghosty/cli.py      → CLI entry point
5. src/ghosty/theme/      → Color palette, styling tokens
6. src/ghosty/catalog/    → 20 action chapters
7. src/ghosty/app/        → Textual app shell & screens
8. pyproject.toml         → Dependencies, build config, tool settings
9. install.py             → Interactive setup script
10. tests/                → Pytest suite
```

---

## Quick-Reference: 10 Most-Used Commands for Agent

```bash
uv run ghosty test           # Self-check
uv run ghosty doctor         # System health
uv run ghosty harden all     # Dry-run full hardening
uv run pytest                # Run tests
uv run ruff check src/       # Lint
uv run mypy src/             # Type-check
uv run python install.py     # Interactive setup
git push origin main         # Deploy
uv build                     # Build distribution
uv publish                   # Push to PyPI
```
