# Product

## Register

product

## Users

macOS power users, privacy engineers, sysadmins, and Apple Silicon developers who want to harden their macOS systems against surveillance, malware, and data leakage. They are comfortable with the terminal but want a guided, visual, and safe experience — not a raw shell script.

## Product Purpose

Ghosty transforms the 919-line macOS Privacy & Security Guide into an interactive, keyboard-first TUI that lets users browse, select, execute, verify, and roll back hardening actions. Every action actually runs the shell — no stubs. Dry-run by default. Snapshots before mutations. One-line rollback.

## Brand Personality

Confident, precise, discreet. Think: Arc browser's command palette meets Gotham's dark terminal. The tool earns trust by being transparent about what it's about to do, showing the command before it runs, and never making a change the user didn't explicitly confirm.

## Anti-references

- Rainbow-vomit colored CLIs that use every ANSI color at once
- Fake "install buttons" that don't actually run anything (like v1)
- Over-engineered TUIs that hide the actual command behind abstractions
- Web-style loading spinners in terminal (use progress bars with ETA)

## Design Principles

1. **Show the command** — never hide what will execute. Every action shows the exact shell command before running.
2. **Dry-run by default** — the default action for any mutation is preview, not execution.
3. **Snapshot → mutate → verify → undo** — every change is a reversible transaction.
4. **Parallel with purpose** — independent actions run concurrently; dependent actions wait. Always show per-action status.
5. **Fail visibly** — when something goes wrong, show stderr and the exit code. Never swallow errors.

## Accessibility & Inclusion

- Full keyboard navigation — no mouse required.
- `NO_COLOR` and `--no-color` support for terminal emulators that don't support ANSI.
- `--json` flag for scripting and CI integration.
- Semantic color usage: cyan=success, amber=warning, red=error, violet=brand.
- CJK-safe widths for international users.
