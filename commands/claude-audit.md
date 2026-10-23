---
description: "claude-audit — list the commands/edits Claude Code ran, from session transcripts"
argument-hint: "[today|session <id|current|last>|sessions [N]] [--project X] [--date D|--since D] [--tools all] [--full]"
---

Run `claude-audit $ARGUMENTS` from the user's current directory using the Bash tool.

`claude-audit` is a Python tool at `~/scripts/claude-audit/bin/claude-audit.py` (symlinked to `~/.local/bin/claude-audit`). This slash command file is at `~/scripts/claude-audit/commands/claude-audit.md` (symlinked to `~/.claude/commands/claude-audit.md`).

Actions:

- **`claude-audit`** or **`claude-audit today`** — today's actions across all projects.
- **`claude-audit session <id|prefix|current|last>`** — one session's actions (`current` = this Claude Code session).
- **`claude-audit sessions [N]`** — the N most recently active sessions.
- **`claude-audit install`** / **`uninstall`** — manage both symlinks. Idempotent.

Read-only: it never modifies transcripts. After it returns, show the output to the user (summarize if very long) and surface the `[ok]` / `[error]` / `[notice]` lines. Do NOT improvise steps the tool does not perform. Never paste its output into external services — transcripts can contain secrets.

Pass through `$ARGUMENTS` verbatim.
