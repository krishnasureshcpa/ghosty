# Ghosty CLI — Cheat Sheet

> **macOS privacy & security TUI** — v2.0.2
> 20+ chapters · 80+ actions · Snapshot → Harden → Verify → Rollback

---

## The Premise

Ghosty reads the [macOS Security & Privacy Guide](https://github.com/drduh/macOS-Security-and-Privacy-Guide)
and turns every recommended command into an **action** you can run from a terminal UI or CLI.

Each action has a **risk level** (1–3):

| Level | Label | What it means | Examples |
|---|---|---|---|
| 3 | **Audit** | Read-only — looks but doesn't touch | `fdesetup status`, `csrutil status` |
| 2 | **Safe** | Changes settings, easily reversible | `defaults write …`, `launchctl disable …` |
| 1 | **Destructive** | Sudo required, may break things | `pfctl -e`, firewall restart, FileVault enable |

---

## Installation

```bash
# Homebrew (recommended)
brew install krishnasureshcpa/tap/ghosty

# OR via uv
uv tool install ghosty-cli

# OR from source
git clone https://github.com/krishnasureshcpa/ghosty
cd ghosty && uv sync
```

**Three entry points** (same thing):

| Command | Purpose |
|---|---|
| `ghosty` | Primary command |
| `ghost` | Alias, does the same |
| `gho` | Shortest alias |

> The old `phantom` binary is removed — migrate to `ghosty`.

---

## The Workflow

```
┌─────────┐     ┌─────────┐     ┌──────────┐     ┌─────────┐
│ DOCTOR  │ ──→ │ HARDEN  │ ──→ │ SNAPSHOT │ ──→ │ ROLLBACK│
│ check   │     │ execute │     │ save     │     │ undo    │
│ health  │     │ actions │     │ state    │     │ changes │
└─────────┘     └─────────┘     └──────────┘     └─────────┘
```

**Always**: `doctor` → `snapshot save` → `harden` → `snapshot save` → `rollback` if needed.

---

## Commands — Quick Reference

### `ghosty doctor` — Health Check

```bash
ghosty doctor                          # Pretty-printed dashboard
ghosty doctor --json                   # Machine-readable (for scripts)
```

Checks: Apple Silicon ✓, SIP enabled ✓, FileVault on/off, Firewall on/off,
Homebrew installed ✓, sudo access, terminal color support.

> **Paranoid tip**: Run this first. If SIP is disabled or FileVault is off,
> those are findings you should know about *before* hardening.

---

### `ghosty harden` — Execute Actions

```bash
ghosty harden all                      # Run EVERYTHING (dry-run by default)
ghosty harden firewall                 # Run actions in "firewall" chapter
ghosty harden all --no-dry-run         # Actually make changes
ghosty harden firewall --no-dry-run    # Make firewall changes only
ghosty harden all --json               # JSON summary output
```

**Target** can be:
- `all` = every action across all chapters
- Any word matching a chapter title (case-insensitive): `firewall`, `dns`, `brew`, `lockdown`…

**Dry-run is ON by default** — it shows what *would* happen without touching anything.
Pass `--no-dry-run` to actually execute.

> **⚠️ SUDO WARNING**: Many actions run `sudo` commands. You'll get prompted for
> your password. Ghosty doesn't store or cache it — macOS handles that.
>
> **Why sudo?** Because changing firewall rules, enabling FileVault, modifying
> `/etc/hosts`, or killing system daemons requires root privileges. Ghosty
> runs the exact same commands you'd type manually — just automated.

---

### `ghosty doctor + harden` — The Safe Way

```bash
# 1. Check your system health
ghosty doctor

# 2. Preview what'll change (DRY RUN — no changes)
ghosty harden all

# 3. Save a snapshot BEFORE making changes
ghosty snapshot save

# 4. Actually execute (you'll be asked for sudo)
ghosty harden all --no-dry-run

# 5. Save another snapshot AFTER (compare later)
ghosty snapshot save

# 6. If something broke — undo
ghosty rollback
```

---

### `ghosty snapshot` — Save & Compare State

```bash
ghosty snapshot save                   # Save current state (FileVault, firewall, etc.)
ghosty snapshot save --json            # JSON path output
ghosty snapshot list                   # List all saved snapshots
```

Snapshots capture: FileVault status, firewall state, timestamp.
They're saved to `~/.config/ghosty/snapshots/snapshot_YYYYMMDD_HHMMSS.json`.

> **Why snapshot?** Before you change anything security-related, you want a
> record of what it looked like before. If something breaks, you can compare
> "before" vs "after".

---

### `ghosty rollback` — Undo Mistakes

```bash
ghosty rollback                        # Undo the LAST action
ghosty rollback 3                      # Undo last 3 actions
ghosty rollback --json                 # JSON output
```

Rollback replays the **inverse** of each action (e.g., if action was `defaults write …`,
rollback runs `defaults delete …`).

> **⚠️ Rollback is best-effort** — not every action has a perfect inverse.
> Actions like FileVault enable have empty rollback (you can't undo encryption
> trivially). Always verify your system still works after a rollback.

---

### `ghosty undo` — Undo a Specific Action

```bash
ghosty undo firewall.stealth           # Undo "firewall.stealth" by action ID
ghosty undo --json                     # JSON output
```

Unlike `rollback` (which undoes the last N), `undo` finds all occurrences of a
specific action ID in your history and rolls them all back.

> **Tip**: Run `ghosty replay` first to see action IDs.

---

### `ghosty replay` — Execution History

```bash
ghosty replay                          # Show last 20 executed actions
ghosty replay --json                   # Full JSON history
```

Shows: timestamp + action ID for everything that was ever executed
(from `~/.config/ghosty/rollback.jsonl`).

---

### `ghosty install` — One-Shot Tool Install

```bash
ghosty install lulu                    # brew install lulu + verify
ghosty install littlesnitch --json
```

Runs `brew install <tool>` under the hood. Supports any Homebrew formula.
Use for installing security tools: `lulu`, `little-snitch`, `blockblock`, `knockknock`, etc.

> **Why `ghosty install` instead of `brew install`?** Nothing — they're identical.
> This command exists so you can install tools from within the Ghosty workflow
> without switching contexts.

---

### `ghosty tui` — Full Terminal App

```bash
ghosty                                 # Opens the TUI (default when no subcommand)
ghosty tui                             # Same thing
```

Inside the TUI, here's what every key does:

| Key | What happens |
|---|---|
| `↑` / `↓` | Move through the action/chapter list |
| `1` – `9` | Jump directly to chapter number |
| `Space` | Toggle selection (select multiple actions) |
| `Enter` | Inspect an action in detail, or execute selected |
| `d` | **Dry-run** — preview what the action would do (no changes) |
| `a` | **Apply** — confirm and execute the action |
| `u` | **Undo** the last applied action |
| `/` | Fuzzy search — type to find actions by name |
| `?` | Help overlay (shows all keybindings) |
| `q` | Quit (only from Home screen) |

**TUI Screens** (you navigate between them naturally):

| Screen | What it shows |
|---|---|
| **Home** | Main menu — chapter list, quick actions |
| **Catalog** | All 20+ chapters with their actions |
| **Detail** | A single action — what it does, what commands it runs |
| **Run** | Execution grid — live output as actions run (4 at a time) |
| **Doctor** | System health dashboard (same as `ghosty doctor`) |
| **Replay** | Execution history (same as `ghosty replay`) |

---

## Sudo Explained

Many actions require `sudo`. Here's why, per category:

| Action type | Why sudo needed |
|---|---|
| Firewall (`socketfilterfw`) | Modifying system network filters |
| PF (`pfctl`) | Packet filter controls the kernel's network stack |
| FileVault (`fdesetup`) | Full-disk encryption requires root |
| `/etc/hosts` modification | System hosts file is root-owned |
| Launchctl disable | Disabling system daemons |
| `csrutil` | System Integrity Protection — the highest security level |

**What happens when sudo is needed:**
- Ghosty runs the command exactly like you'd type it: `sudo pfctl -e`
- macOS shows a dialog / terminal prompt for your password
- After authentication, the command runs with root privileges
- Ghosty does **not** store, cache, or log your password

> **Paranoid reassurance**: Ghosty doesn't do anything you couldn't do by hand.
> It just automates the 919-line guide so you don't have to type 80+ commands
> one by one. Every command is visible in the dry-run preview before execution.

---

## Environment Variables

| Variable | What it does | Default |
|---|---|---|
| `GHOSTY_CHEATSHEET` | Custom path to your privacy guide | `~/.config/ghosty/cheatsheet.md` |
| `NO_COLOR` | Disable colored output (set to any value) | — |

> **If the cheatsheet isn't found**: Set `GHOSTY_CHEATSHEET=/path/to/your/MacOS-Privacy-CheatSheet.md`
> before running ghosty.

---

## File Locations

| What | Where |
|---|---|
| Cached catalog | `~/.config/ghosty/catalog.json` |
| Snapshots | `~/.config/ghosty/snapshots/snapshot_*.json` |
| Rollback store | `~/.config/ghosty/rollback.jsonl` |
| Cheatsheet (default) | `~/.config/ghosty/cheatsheet.md` (or set `$GHOSTY_CHEATSHEET`) |

---

## Troubleshooting

### "Command not found" after install

```bash
# If you used uv:
uv tool install ghosty-cli && uv tool update-shell

# If you cloned the repo:
cd ghosty && uv sync && uv run ghosty
```

### "TUI not available"

```bash
uv sync                            # Install all dependencies
```

### "Error: ghosty requires macOS"

You're on Linux or Windows. Ghosty only works on macOS — it calls macOS-specific
binaries (`csrutil`, `fdesetup`, `socketfilterfw`, `pfctl`).

### Action X failed

```bash
# 1. Check the error:
ghosty harden firewall --no-dry-run

# 2. If it's a sudo timeout — just re-run, macOS cached your creds
# 3. If a setting was already applied — that's fine, some actions aren't idempotent
# 4. Worst case — rollback:
ghosty rollback
```

### Dry-run says it'll do something scary

1. Read the action description carefully
2. Run `ghosty doctor` first to see current state
3. `ghosty snapshot save` to record before-state
4. Only then `ghosty harden X --no-dry-run`

---

## The 30-Second Paranoid Routine

```bash
ghosty doctor                           # 1. Check health
ghosty snapshot save                     # 2. Save state
ghosty harden all --no-dry-run           # 3. Harden everything
ghosty snapshot save                     # 4. Save new state
ghosty replay                            # 5. Review what ran
```

---

> **Don't trust? Verify.** Every action has `verify_ops` that check the result.
> Use `--json` for scriptable audit trails. The catalog source is open —
> read it at `src/ghosty/catalog/__init__.py`.
