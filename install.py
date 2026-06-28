#!/usr/bin/env python3
"""
Ghosty — Interactive Setup Script

Usage:
    python install.py

Scans your system, installs missing dependencies (Homebrew → uv → Python),
and configures Ghosty globally or in a virtual environment.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# ANSI styling (no Rich dependency here — this runs before the venv exists)
# ---------------------------------------------------------------------------

VIOLET = "\033[38;5;99m"
CYAN = "\033[38;5;51m"
GREEN = "\033[38;5;46m"
AMBER = "\033[38;5;214m"
RED = "\033[38;5;196m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"
LOGO = (
    f"{VIOLET}"
    "  ╔══════════════════════════════════╗\n"
    "  ║     👻  G H O S T Y   v2       ║\n"
    "  ║  macOS Privacy & Security TUI   ║\n"
    "  ╚══════════════════════════════════╝"
    f"{RESET}"
)

PROJECT_ROOT = Path(__file__).resolve().parent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def print_step(label: str, detail: str = "", status: str = "pending") -> None:
    icon = {"ok": "✓", "fail": "✗", "pending": "·", "info": "→"}.get(status, "·")
    color = {"ok": GREEN, "fail": RED, "pending": DIM, "info": CYAN}.get(status, DIM)
    print(f"  {color}{icon}{RESET} {BOLD}{label}{RESET} {DIM}{detail}{RESET}")


def ask_yes_no(prompt: str, default: bool = True) -> bool:
    hint = "Y/n" if default else "y/N"
    answer = input(f"\n  {CYAN}?{RESET} {prompt} [{hint}] ").strip().lower()
    if answer in ("y", "yes"):
        return True
    if answer in ("n", "no"):
        return False
    return default


def ask_choice(prompt: str, options: list[str], default: int = 0) -> str:
    print(f"\n  {CYAN}?{RESET} {prompt}")
    for i, opt in enumerate(options, 1):
        marker = f"{BOLD}▶{RESET}" if i - 1 == default else " "
        print(f"    {marker} {i}. {opt}")
    raw = input(f"  {' ' * 3}Choice [1-{len(options)}] (default {default + 1}): ").strip()
    if raw.isdigit() and 1 <= int(raw) <= len(options):
        return options[int(raw) - 1]
    return options[default]


def run(cmd: list[str], timeout: int = 120, check: bool = False) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=check)
    except FileNotFoundError:
        return subprocess.CompletedProcess(cmd, 1, "", "command not found")


# ---------------------------------------------------------------------------
# Dependency checks
# ---------------------------------------------------------------------------


def check_macos() -> bool:
    print_step("Platform", sys.platform, "info")
    if sys.platform != "darwin":
        print_step("macOS required", "this tool only runs on macOS", "fail")
        return False
    print_step("macOS", "detected ✓", "ok")
    return True


def check_homebrew() -> Path | None:
    brew = shutil.which("brew") or "/opt/homebrew/bin/brew"
    if Path(brew).exists():
        print_step("Homebrew", str(brew), "ok")
        return Path(brew)
    print_step("Homebrew", "not found", "fail")
    return None


def check_python() -> tuple[str, bool]:
    v = sys.version_info
    ok = v.major >= 3 and v.minor >= 12
    label = f"{v.major}.{v.minor}.{v.micro}"
    print_step("Python", f"{label} {'✓' if ok else '✗ (3.12+ needed)'}", "ok" if ok else "fail")
    if not ok:
        print(f"  {DIM}  This script itself is running Python {label}, which is too old.{RESET}")
        print(f"  {DIM}  We'll install Python 3.12+ and you'll need to re-run.{RESET}")
    return label, ok


def check_uv() -> Path | None:
    uv = shutil.which("uv")
    # Also check common locations the current PATH may not include
    if not uv:
        for candidate in [Path.home() / ".local" / "bin" / "uv",
                          Path("/opt/homebrew/bin/uv"),
                          Path("/usr/local/bin/uv"),
                          Path.home() / ".cargo" / "bin" / "uv"]:
            if candidate.exists():
                uv = str(candidate)
                break
    if uv:
        r = run([uv, "--version"], timeout=10)
        print_step("uv", r.stdout.strip() or str(uv), "ok")
        return Path(uv)
    print_step("uv", "not found", "fail")
    return None


def check_git() -> bool:
    git = shutil.which("git")
    if git:
        print_step("Git", str(git), "ok")
        return True
    print_step("Git", "not found", "fail")
    return False


# ---------------------------------------------------------------------------
# Installers
# ---------------------------------------------------------------------------


def install_homebrew() -> bool:
    print()
    print(f"  {AMBER}── Installing Homebrew ──────────────────────────{RESET}")
    if not ask_yes_no("Homebrew is missing. Install it?"):
        return False
    cmd = [
        "/bin/bash",
        "-c",
        "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)",
    ]
    print(f"  {DIM}Running Homebrew installer (may take a few minutes)...{RESET}")
    r = subprocess.run(cmd, timeout=300)
    if r.returncode != 0:
        print_step("Homebrew install", "failed", "fail")
        return False
    print_step("Homebrew", "installed ✓", "ok")
    return True


def install_uv_via_homebrew(brew: Path) -> bool:
    print()
    print(f"  {AMBER}── Installing uv via Homebrew ────────────────────{RESET}")
    r = run([str(brew), "install", "uv"], timeout=120)
    if r.returncode == 0:
        print_step("uv", "installed via Homebrew ✓", "ok")
        return True
    print_step("uv (brew)", r.stderr.strip()[:80], "fail")
    return False


def install_uv_via_curl() -> bool:
    print()
    print(f"  {AMBER}── Installing uv via curl ────────────────────────{RESET}")
    if not ask_yes_no("Install uv directly (official installer)?"):
        return False
    r = subprocess.run(
        ["/bin/bash", "-c", "$(curl -fsSL https://astral.sh/uv/install.sh)"],
        timeout=120,
    )
    if r.returncode == 0:
        print_step("uv", "installed ✓ (restart shell or source ~/.zshrc)", "ok")
        return True
    print_step("uv install", "failed", "fail")
    return False


def install_python_via_homebrew(brew: Path) -> bool:
    print()
    print(f"  {AMBER}── Installing Python 3.12+ via Homebrew ──────────{RESET}")
    r = run([str(brew), "install", "python@3.12"], timeout=300)
    if r.returncode == 0:
        print_step("Python 3.12", "installed ✓", "ok")
        return True
    print_step("Python install", r.stderr.strip()[:80], "fail")
    return False


# ---------------------------------------------------------------------------
# Install Ghosty
# ---------------------------------------------------------------------------


def install_global(uv: Path) -> bool:
    print()
    print(f"  {AMBER}── Installing Ghosty globally ────────────────────{RESET}")
    print(f"  {DIM}Running: uv tool install .{RESET}")
    r = run([str(uv), "tool", "install", str(PROJECT_ROOT)], timeout=180)
    if r.returncode != 0:
        print_step("Global install", r.stderr.strip()[:120], "fail")
        return False
    # Verify the command is now available
    ghosty = shutil.which("ghosty")
    if ghosty:
        print_step("Ghosty", f"installed at {ghosty} ✓", "ok")
    else:
        # Try common locations
        for p in [
            Path.home() / ".local" / "bin" / "ghosty",
            Path.home() / ".cargo" / "bin" / "ghosty",
        ]:
            if p.exists():
                print_step("Ghosty", f"installed at {p} ✓", "ok")
                break
        else:
            print_step("Ghosty", "installed but not on PATH — may need shell restart", "info")
    return True


def install_local_venv(uv: Path) -> bool:
    print()
    print(f"  {AMBER}── Setting up local virtual environment ──────────{RESET}")
    r = run([str(uv), "sync"], cwd=str(PROJECT_ROOT), timeout=180)
    if r.returncode != 0:
        print_step("uv sync", r.stderr.strip()[:120], "fail")
        return False
    print_step("Virtual env", "ready ✓", "ok")

    # Suggest alias
    shell = os.environ.get("SHELL", "")
    rc_file = ""
    alias_line = f"alias ghosty='{PROJECT_ROOT}/.venv/bin/ghosty'"
    if "zsh" in shell:
        rc_file = str(Path.home() / ".zshrc")
    elif "bash" in shell:
        rc_file = str(Path.home() / ".bashrc")

    if rc_file and (rc_path := Path(rc_file)).exists() and alias_line not in rc_path.read_text() and ask_yes_no(f"Add alias to {rc_file} so 'ghosty' works everywhere?"):
        with open(rc_path, "a") as f:
            f.write(f"\n# Ghosty alias\n{alias_line}\n")
        print_step("Shell alias", f"added to {rc_file} (restart shell or source it)", "ok")
    return True


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------


def run_self_test(uv: Path | None, mode: str) -> bool:
    print()
    print(f"  {AMBER}── Running self-test ──────────────────────────────{RESET}")
    if mode == "global" and shutil.which("ghosty"):
        cmd = [shutil.which("ghosty"), "test"]
    elif (PROJECT_ROOT / ".venv" / "bin" / "ghosty").exists():
        cmd = [str(PROJECT_ROOT / ".venv" / "bin" / "ghosty"), "test"]
    elif uv:
        cmd = [str(uv), "run", "--directory", str(PROJECT_ROOT), "python", "-m", "ghosty", "test"]
    else:
        cmd = [sys.executable, "-m", "ghosty", "test"]

    print(f"  {DIM}Running: {' '.join(cmd)}{RESET}")
    print()
    r = subprocess.run(cmd, timeout=60, cwd=str(PROJECT_ROOT))
    if r.returncode == 0:
        print(f"  {GREEN}✓{RESET} {BOLD}All checks passed!{RESET}")
    else:
        print(f"  {RED}✗{RESET} {BOLD}Self-test failed (exit code {r.returncode}){RESET}")
    return r.returncode == 0


# ---------------------------------------------------------------------------
# Shell completion hint
# ---------------------------------------------------------------------------


def suggest_shell_completion() -> None:
    print()
    print(f"  {CYAN}→{RESET} {BOLD}Shell completion (optional):{RESET}")
    shell = os.environ.get("SHELL", "")
    if "zsh" in shell:
        print("    Add to ~/.zshrc:")
        print(f"      {DIM}eval \"$(_GHOSTY_COMPLETE=zsh_source ghosty)\"{RESET}")
    elif "bash" in shell:
        print("    Add to ~/.bashrc:")
        print(f"      {DIM}eval \"$(_GHOSTY_COMPLETE=bash_source ghosty)\"{RESET}")


# ---------------------------------------------------------------------------
# Welcome screen & top 3 commands
# ---------------------------------------------------------------------------


def show_welcome() -> None:
    print()
    print(f"  {VIOLET}{'═' * 48}{RESET}")
    print(f"  {VIOLET}  👻  Welcome to Ghosty!  Your macOS is about{RESET}")
    print(f"  {VIOLET}  to get a whole lot safer.                  {RESET}")
    print(f"  {VIOLET}{'═' * 48}{RESET}")
    print()
    print(f"  {BOLD}Top 3 commands to get started:{RESET}")
    print()
    print(f"  {CYAN}1{VIOLET}.{RESET} {BOLD}ghosty doctor{RESET}")
    print(f"     {DIM}Scan your Mac's current security posture — SIP,{RESET}")
    print(f"     {DIM}FileVault, Firewall, and more in one glance.{RESET}")
    print()
    print(f"  {CYAN}2{VIOLET}.{RESET} {BOLD}ghosty harden all{RESET}")
    print(f"     {DIM}Fire off every hardening action across all 20{RESET}")
    print(f"     {DIM}chapters. Dry-run by default — safe to preview.{RESET}")
    print()
    print(f"  {CYAN}3{VIOLET}.{RESET} {BOLD}ghosty (no args){RESET}")
    print(f"     {DIM}Launch the full Textual TUI — browse, select,{RESET}")
    print(f"     {DIM}and execute hardening from a keyboard-first UI.{RESET}")
    print()
    print(f"  {GREEN}  ✓  Setup complete. Ghosty is ready to roll.{RESET}")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print()
    print(LOGO)
    print()
    print(f"  {DIM}Interactive setup · macOS Privacy & Security TUI{RESET}")
    print(f"  {DIM}Repo: github.com/krishnasureshcpa/ghosty{RESET}")
    print()

    # --- Phase 1: System scan ---
    print(f"  {BOLD}── System scan ──────────────────────────────────{RESET}")

    if not check_macos():
        sys.exit(1)

    _, python_ok = check_python()
    git_ok = check_git()
    brew = check_homebrew()
    uv = check_uv()

    if not git_ok:
        print()
        print_step("Git required", "install Xcode Command Line Tools: xcode-select --install", "fail")
        if not ask_yes_no("Continue anyway? (some features may not work)", default=False):
            sys.exit(1)

    # --- Phase 2: Resolve missing deps ---
    needs_python = not python_ok
    needs_uv = uv is None
    needs_brew = brew is None

    if (needs_python or needs_uv) and needs_brew:
        print()
        print(f"  {AMBER}── Homebrew is needed for dependencies ─────────{RESET}")
        if install_homebrew():
            brew = check_homebrew()
            needs_brew = False
        else:
            print_step("Cannot proceed", "Homebrew is required to install dependencies", "fail")
            sys.exit(1)

    if needs_python and brew:
        install_python_via_homebrew(brew)
        # Re-check after install
        _, python_ok = check_python()
        if not python_ok:
            py_path = shutil.which("python3.12") or shutil.which("python3")
            if py_path:
                print()
                print(f"  {AMBER}── Python 3.12+ installed, but this session is running an older version ──{RESET}")
                print(f"  {DIM}  Re-run this script with the new Python:{RESET}")
                print(f"  {CYAN}    {py_path} install.py{RESET}")
                print()
                if ask_yes_no("Re-run with the new Python now?"):
                    subprocess.run([py_path, __file__])
                sys.exit(0)
            else:
                print()
                print_step("Python", "3.12+ was installed but not found on PATH. Restart your terminal and re-run install.py", "fail")
                sys.exit(1)

    if needs_uv and brew:
        if not install_uv_via_homebrew(brew):
            install_uv_via_curl()
        uv = check_uv()

    if uv is None:
        print()
        print_step("uv required", "Cannot install Ghosty without uv. Install manually:\n    curl -fsSL https://astral.sh/uv/install.sh | bash", "fail")
        sys.exit(1)

    # --- Phase 3: Install mode ---
    print()
    print(f"  {BOLD}── Installation mode ────────────────────────────{RESET}")
    mode = ask_choice(
        "How would you like to install Ghosty?",
        ["Global — available everywhere as 'ghosty'",
         "Local — isolated virtual environment in this repo"],
        default=0,
    )
    is_global = "Global" in mode

    if is_global:
        ok = install_global(uv)
        if not ok:
            print()
            print(f"  {AMBER}Global install failed. Falling back to local venv...{RESET}")
            is_global = False
            ok = install_local_venv(uv)
    else:
        ok = install_local_venv(uv)

    if not ok:
        print()
        print_step("Installation", "failed", "fail")
        sys.exit(1)

    # --- Phase 4: Verify ---
    run_self_test(uv, "global" if is_global else "local")

    # --- Phase 5: Shell extras ---
    suggest_shell_completion()

    # --- Phase 6: Welcome ---
    show_welcome()


if __name__ == "__main__":
    main()
