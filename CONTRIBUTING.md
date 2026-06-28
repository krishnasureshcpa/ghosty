# Contributing to Phantom

Thanks for your interest! Phantom is privacy-hardening tooling and we take
quality seriously.

## Quick start

```bash
git clone https://github.com/krishnasureshcpa/ghosty
cd ghosty
uv sync
uv run phantom
```

## Making changes

1. Fork the repo and create a feature branch from `main`.
2. Run `ruff check src/` before committing.
3. Add tests for any new catalog actions or backends.
4. Update `README.md` if you add a feature visible to users.

## Coding conventions

- Python 3.12+, strict `mypy`, `ruff`-clean.
- Every catalog action requires a verification op that proves the setting changed.
- Use `from __future__ import annotations` in every module.
- Keep individual files under 400 lines.

## Pull request checklist

- [ ] `ruff check .` passes
- [ ] `mypy src/` — no new errors
- [ ] Tests pass: `pytest -v`
- [ ] README updated if behaviour changed
- [ ] CHANGELOG updated

## Reporting issues

See [ISSUE_TEMPLATE](.github/ISSUE_TEMPLATE/bug_report.md). For security
issues, read [SECURITY.md](SECURITY.md) instead.
