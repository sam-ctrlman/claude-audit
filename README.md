# claude-audit

List every action Claude Code took (Bash commands, file edits/writes), read-only from the
session transcripts in `~/.claude/projects/*/*.jsonl` (+ `*/subagents/*.jsonl`).
Useful for reviewing what Claude ran in auto mode.

## Install

```sh
git clone <remote-url> ~/scripts/claude-audit
python3 ~/scripts/claude-audit/bin/claude-audit.py install
```

After install, `claude-audit` works in any shell and `/claude-audit` works in Claude Code.

## Actions

| Action | What it does |
|--------|-------------|
| `claude-audit` / `claude-audit today` | Today's actions, all projects (`run` = alias) |
| `claude-audit session <id\|prefix\|current\|last>` | One session. `current` = `$CLAUDE_CODE_SESSION_ID` (inside Claude Code); `last` = newest session for `$PWD` |
| `claude-audit sessions [N]` | N most recently active sessions (default 10): uuid, last active, project, #actions, first prompt |
| `claude-audit install` | Create bin + Claude command symlinks |
| `claude-audit uninstall` | Remove both symlinks |

Options: `--tools Bash,Edit,Write,NotebookEdit` (default) or `--tools all`, `--project <substr>`,
`--date YYYY-MM-DD` / `--since YYYY-MM-DD`, `--full` (no 160-char truncation), `--no-subagents`.

Output: `time  project  session[sub]  tool  ✓|✗|·  command-or-path`
(`✗` = tool result was an error, `·` = no result recorded, e.g. interrupted).

Exit codes: 0 ok (also when nothing matches), 1 unknown/ambiguous session, 2 bad args.

⚠ Transcripts may contain secrets that appeared in commands. Output goes to your terminal only;
don't paste it anywhere public.

## Layout

```
~/scripts/claude-audit/
├── README.md
├── bin/claude-audit.py
└── commands/claude-audit.md
```
