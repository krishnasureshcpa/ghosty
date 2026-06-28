# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 2.x     | ✅        |
| < 2.0   | ❌        |

## Reporting a vulnerability

Phantom executes system commands (`brew install`, `defaults write`, etc.) and
operates with elevated privileges on some operations. If you find a security
issue — especially one that could lead to privilege escalation, data loss, or
unexpected command execution — please **do not file a public issue**.

Email: krishnasureshcpa@users.noreply.github.com

You should receive a response within 48 hours. If you don't, follow up.

## What to include

- Steps to reproduce
- Phantom version (`phantom --version`)
- macOS version (`sw_vers`)
- Whether you were running with or without `sudo`

## Scope

In scope: the Phantom TUI, catalog parsing, runner, and all backends.

Out of scope: third-party tools Phantom invokes (`brew`, `csrutil`, etc.).
