# Export Sessions — Ghosty

## Convention
- **Folder**: `export-sessions-ghosty/` in the project root
- **File**: `export-DD-MM-YYYY-HH-MM-appname.md` (e.g. `export-28-06-2026-07-59-ghosty.md`)
- **PDF companion**: Same name, `.pdf` extension (pandoc + xelatex)
- **Purpose**: Persistent handoff/session export so any AI agent can resume exactly where the last session stopped

## How AI Agents Should Use This
1. On session START, scan for the latest file by date in filename:
   ```bash
   ls -t export-sessions-ghosty/export-*.md 2>/dev/null | head -1
   ```
2. Read that file to restore full context.
3. On session EXIT (or when tokens reach ~5% remaining), automatically run:
   ```bash
   ./export-sessions-ghosty/auto-handoff.sh
   ```
   This creates a timestamped `.md` + `.pdf` pair.

## auto-handoff.sh
The script in this directory:
- Captures `git log --oneline -20`, `git status`, `git diff --stat`
- Generates a markdown handoff with timestamp, work summary, pending items
- Converts to PDF via pandoc + xelatex
- Names files per the convention above

## Prerequisites (for PDF generation)
- `pandoc` (brew install pandoc)
- `xelatex` (part of MacTeX: brew install --cask mactex-no-gui)
- These are already installed on this machine.

## Token Exhaustion Protocol
When an AI agent detects it has ~5% or fewer tokens remaining in its context window:
1. STOP all ongoing work immediately
2. Run the auto-handoff script
3. Present the handoff to the user
4. Suggest the user start a new session and provide the handoff file path
