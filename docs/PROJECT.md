# claude-audit

<!-- created by /memlayout 2026-10-30 · board prefix TOOL-AUDIT · workspace tools -->

## Goal
Read-only CLI & live tail -f monitor to audit every Bash command, file edit, and subagent action executed by Claude Code.

## Users
A developer who runs Claude Code on their own machine and wants this step done the same way every time.

## Scope
- In: the commands in `README.md`, `claude-audit install` / `uninstall` (symlinks onto PATH and into `~/.claude`).
- Out (non-goals): anything that needs a server or a network service of its own.

## Depends on / used by
Other tools in the workspace only through their CLI. See `~/tools/docs/PROJECTS.md`.
