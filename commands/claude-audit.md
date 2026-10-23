---
description: "TODO: claude-audit — describe what this slash command does"
argument-hint: "[run|install|uninstall]"
---

Run `claude-audit $ARGUMENTS` from the user's current directory using the Bash tool.

`claude-audit` is a Python tool at `~/scripts/claude-audit/bin/claude-audit.py` (symlinked to `~/.local/bin/claude-audit`). This slash command file is at `~/scripts/claude-audit/commands/claude-audit.md` (symlinked to `~/.claude/commands/claude-audit.md`).

Actions:

- **`claude-audit`** or **`claude-audit run`** — TODO: the workflow this tool automates (not implemented yet — edit `cmd_run()` in the script).
- **`claude-audit install`** — create both symlinks (bin + Claude command). Idempotent.
- **`claude-audit uninstall`** — remove both symlinks. Idempotent.

After it returns, surface the `[ok]` / `[error]` / `[notice]` log lines to the user. Do NOT improvise steps the tool does not perform — the tool owns its workflow.

Pass through `$ARGUMENTS` verbatim. Valid args: `run`, `install`, `uninstall`, or empty (defaults to `run`).
