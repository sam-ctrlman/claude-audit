# claude-audit

<!-- created by /memlayout 2026-10-30 · board prefix TOOL-AUDIT · workspace tools -->

## Goal
Lists every action Claude Code took (Bash, Edit, Write, …) from the session transcripts. Read-only.

## Users
A developer who runs Claude Code on their own machine and wants this step done the same way every time.

## Scope
- In: the commands in `README.md`, `claude-audit install` / `uninstall` (symlinks onto PATH and into `~/.claude`).
- Out (non-goals): anything that needs a server or a network service of its own.

## Depends on / used by
Other tools in the workspace only through their CLI. See `~/tools/docs/PROJECTS.md`.
