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
| `claude-audit today -t` / `claude-audit session last -t` | Live log like `tail -f`: last `-n` rows (default 20), then new actions as they happen; Ctrl-C stops (exit 130) |
| `claude-audit install` | Create bin + Claude command symlinks |
| `claude-audit uninstall` | Remove both symlinks |

Options: `--tools Bash,Edit,Write,NotebookEdit` (default) or `--tools all`, `--project <substr>`,
`--date YYYY-MM-DD` / `--since YYYY-MM-DD`, `--full` (no cut), `-w/--width N` (cut command text
at N chars; default 160, with `-t` the terminal width), `--no-subagents`.
Live log (`-t`, aliases `-f`, `--tail`, `--follow`): `-n/--lines N` backlog rows, `--interval SEC` (default 2).

Output: `time  project  session[sub]  tool  ✓|✗|·|…  command-or-path`
(`✗` = tool result was an error, `·` = no result recorded, e.g. interrupted or still running;
`…` = `-t` only: a call still running after 3 s, its ✓/✗ row follows when it finishes).
✓/✗ is the final exit status of the whole command, so a failing step inside `a; b | head` can still show ✓.

```sh
claude-audit today -t                      # every project, live
claude-audit session last -t -n 50         # newest session for $PWD, 50-row backlog
claude-audit -t --project my-app --tools all --full
```
`session last` is resolved once at start, so `-t` keeps following that session. With `today -t`,
new sessions are picked up automatically and the log keeps running past midnight.

Exit codes: 0 ok (also when nothing matches), 1 unknown/ambiguous session, 2 bad args.

⚠ Transcripts may contain secrets that appeared in commands. Output goes to your terminal only;
don't paste it anywhere public. A `-t` pane shows commands live, so don't screen-share it.

## Layout

```
~/scripts/claude-audit/
├── README.md
├── bin/claude-audit.py
└── commands/claude-audit.md
```
