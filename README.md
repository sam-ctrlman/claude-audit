# claude-audit

TODO: one-line description of what claude-audit automates.

## Install

```sh
git clone <remote-url> ~/scripts/claude-audit
python3 ~/scripts/claude-audit/bin/claude-audit.py install
```

After install, `claude-audit` works in any shell and `/claude-audit` works in Claude Code.

## Actions

| Action | What it does |
|--------|-------------|
| `claude-audit` / `claude-audit run` | TODO: the automated workflow |
| `claude-audit install` | Create bin + Claude command symlinks |
| `claude-audit uninstall` | Remove both symlinks |

## Layout

```
~/scripts/claude-audit/
├── README.md
├── bin/claude-audit.py
└── commands/claude-audit.md
```

## Next steps after scaffolding

1. Edit `bin/claude-audit.py` — replace the `cmd_run()` body with the deterministic
   steps this tool should automate. Keep each step idempotent (start with a
   `[skip]` fast-path when the work is already done).
2. Update this README and the `description:` in `commands/claude-audit.md`.
3. `git add -A && git commit` the changes.
4. (Optional) add a remote and `git push -u origin main`.
