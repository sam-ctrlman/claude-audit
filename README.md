# claude-audit

**Fast, read-only CLI tool to audit, inspect, and live-stream every action Claude Code executes on your machine.**

When running **Claude Code** (especially in autonomous / auto-accept mode), keeping track of executed `Bash` commands, modified files, and spawned subagents can be difficult. `claude-audit` parses local Claude Code session transcripts (`~/.claude/projects/*/*.jsonl` and `*/subagents/*.jsonl`) in real time so you can review command history, audit file writes, and monitor live agent activity directly from your terminal.

---

## Why Use `claude-audit`?

- **100% Read-Only & Safe:** Inspects local `.jsonl` session transcripts without modifying Claude Code state or interfering with active sessions.
- **Built for Auto-Mode Auditing:** Instantly verify every `Bash`, `Edit`, `Write`, and `NotebookEdit` operation Claude executed while unattended.
- **Live Terminal Streaming (`tail -f` style):** Watch commands and subagent tasks execute in real time in a split terminal or `tmux` pane.
- **Subagent Visibility:** Automatically tracks actions performed by nested subagents (`*/subagents/*.jsonl`) alongside the parent session.
- **Dual Interface:** Run `claude-audit` from any standard shell, or invoke `/claude-audit` directly inside an active Claude Code prompt.

---

## Example Output

```text
14:02:11  my-app  8f9a2c10       Bash   ✓  npm run test:unit
14:02:18  my-app  8f9a2c10[sub]  Edit   ✓  src/auth/middleware.ts
14:02:24  my-app  8f9a2c10       Bash   ✗  npx prisma migrate deploy
14:02:29  my-app  8f9a2c10       Bash   …  docker compose build --no-cache
```

**Output Columns:**
`time  project  session[sub]  tool  status  command-or-path`

| Status Symbol | Meaning |
| :---: | :--- |
| `✓` | **Success:** The tool call completed and returned a normal exit status. |
| `✗` | **Error:** The tool call failed or returned a non-zero error state. |
| `·` | **Incomplete:** No result recorded (e.g., command was interrupted or is still running in static view). |
| `…` | **Running (Live Mode `-t` only):** A tool call has been running for more than 3 seconds. Its final `✓` or `✗` row prints automatically once it finishes. |

> **Note on Shell Pipelines:** `✓` and `✗` reflect the final exit status of the entire command string. A failing step inside an unhandled chain or pipe (such as `cmd_a; cmd_b | head`) may still report `✓` if the final command succeeded.

---

## Installation

Clone the repository and run the built-in installer to symlink both the CLI binary and the Claude Code slash command:

```sh
git clone <remote-url> ~/tools/projects/claude-audit
python3 ~/tools/projects/claude-audit/bin/claude-audit.py install
```

Once installed:
1. Run `claude-audit` from **any terminal shell**.
2. Run `/claude-audit` directly **inside Claude Code**.

To remove the symlinks at any time:
```sh
claude-audit uninstall
```

---

## Core Commands

| Command | Description |
| :--- | :--- |
| `claude-audit` or `claude-audit today` | List all actions recorded today across all projects (`run` is supported as an alias). |
| `claude-audit session <target>` | Inspect a single session. `<target>` accepts a full UUID, UUID prefix, `current` (reads `$CLAUDE_CODE_SESSION_ID` inside Claude Code), or `last` (newest session for `$PWD`). |
| `claude-audit sessions [N]` | List the `N` most recently active sessions (default: `10`), displaying UUID, last active timestamp, project name, total action count, and initial prompt. |
| `claude-audit today -t` | Stream a live log (`tail -f` mode) across all projects. Prints the last `-n` actions (default: `20`), then streams new actions in real time. |
| `claude-audit session last -t` | Stream a live log locked to the newest session in your current working directory (`$PWD`). |
| `claude-audit install` | Create the shell binary symlink and Claude Code `/claude-audit` command symlink. |
| `claude-audit uninstall` | Remove both symlinks cleanly. |

---

## Options & Filtering Flags

Customize what `claude-audit` displays using the following flags:

| Flag / Option | Default | Description |
| :--- | :--- | :--- |
| `--tools <list\|all>` | `Bash,Edit,Write,NotebookEdit` | Comma-separated list of tools to audit, or `all` to include read/search tools (`Read`, `Grep`, `Glob`, etc.). |
| `--project <substr>` | *All projects* | Filter log entries to projects matching the given substring. |
| `--date YYYY-MM-DD` | *Today* | Show actions from a specific calendar date. |
| `--since YYYY-MM-DD` | *None* | Show all actions recorded on or after a specific date. |
| `--full` | `false` | Print complete command strings and file paths without line truncation. |
| `-w`, `--width <N>` | `160` (or TTY width in `-t`) | Truncate command text at `N` characters. |
| `-S`, `--scroll` | `false` | Full lines inside `less -S`: `←`/`→` scroll sideways, `/` search, `q` quit. With `-t`: `Ctrl-C` pauses the follow, `F` resumes, `q` quits (exit `0`). Without a terminal it prints like `--full`. Not with `-w`. |
| `--no-subagents` | `false` | Exclude actions executed by subagents (`*/subagents/*.jsonl`). |
| `-t`, `-f`, `--tail`, `--follow` | `false` | Enable live-streaming mode (`Ctrl-C` to stop, exits with code `130`). |
| `-n`, `--lines <N>` | `20` | Number of historical backlog rows to display when starting `-t` live mode. |
| `--interval <SEC>` | `2` | Polling interval in seconds when watching files in `-t` live mode. |

---

## Common Auditing Workflows

### 1. Monitor Claude Code Auto-Mode in Real Time
Open a side-by-side terminal pane and stream every project's activity live. `today -t` automatically detects newly created sessions and continues streaming seamlessly past midnight:
```sh
claude-audit today -t
```

### 2. Follow Only the Active Project Session
Lock onto the latest session for your current working directory with a 50-line history backlog (`session last` resolves once at startup so `-t` stays locked to that specific session):
```sh
claude-audit session last -t -n 50
```

### 3. Deep-Dive Audit on a Specific Project
View every tool call (including reads and searches) without character truncation for a specific repository:
```sh
claude-audit -t --project my-app --tools all --full
```

Keep long commands on one line and scroll sideways instead of wrapping:
```sh
claude-audit session last -S
claude-audit today -t -S
```

### 4. Review Recent Sessions Before Resuming Work
Check the last 15 sessions to see action counts and the initial prompt that started each run:
```sh
claude-audit sessions 15
```

---

## Security & Privacy Warning

> [!WARNING]
> **Transcripts May Contain Plaintext Secrets**
> Claude Code session logs record exact command arguments, environment variables, and tokens passed via the command line. 
> - `claude-audit` prints strictly to your local `stdout` and never transmits data externally.
> - **Redaction:** Always review and sanitize output before pasting audit logs into public issues, PRs, or chat channels.
> - **Screen Sharing:** Avoid keeping an active `claude-audit -t` pane visible during live streams or screen shares, as secret values in commands will appear in real time.

---

## Exit Codes & Project Layout

### Exit Codes
* `0` — Success (including when a valid query returns zero matching rows).
* `1` — Unknown or ambiguous session ID/prefix.
* `2` — Invalid command-line arguments.
* `130` — Live stream (`-t`) terminated by user via `Ctrl-C`.

### Directory Structure
```text
~/tools/projects/claude-audit/
├── README.md
├── bin/claude-audit.py       # Core CLI executable & JSONL parser
└── commands/claude-audit.md  # Slash-command definition for Claude Code
```

---

## Frequently Asked Questions (FAQ)

**Where does Claude Code store its command and session logs?**  
Claude Code stores session transcripts locally as JSON Lines files inside `~/.claude/projects/<project-name>/<session-uuid>.jsonl`, with subagent tasks stored in `~/.claude/projects/<project-name>/<session-uuid>/subagents/*.jsonl`.

**How can I see what Bash commands Claude Code ran in auto mode?**  
Run `claude-audit` (or `claude-audit session last`) in your terminal. By default, it filters out noisy read operations and highlights state-changing tools (`Bash`, `Edit`, `Write`, `NotebookEdit`) alongside their execution status (`✓` or `✗`).

**Does `claude-audit` slow down or lock Claude Code?**  
No. `claude-audit` opens `.jsonl` transcript files in strictly read-only mode, making it safe to run concurrently alongside active Claude Code sessions and subagents.
