#!/usr/bin/env python3
"""claude-audit — list every action Claude Code took, from the session transcripts.

Reads ~/.claude/projects/*/*.jsonl (plus */subagents/*.jsonl) read-only and
prints one line per tool call: local time, project, session, tool, ✓/✗, and
the command or file path.

Usage:
  claude-audit                          # = today
  claude-audit today                    # today's actions, all projects
  claude-audit session <id|prefix|current|last>
  claude-audit sessions [N]             # N newest sessions (default 10)
  claude-audit install                  # symlink into ~/.local/bin + ~/.claude/commands
  claude-audit uninstall                # remove those symlinks
  claude-audit --help

Options: --tools Bash,Edit,... | all, --project <substr>, --date/--since
YYYY-MM-DD, --full, --no-subagents.

Scaffolded by `forge`. The tool name is derived from the repo directory, so
nothing here is hardcoded — rename the repo and it follows.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from datetime import date, datetime
from pathlib import Path


def log(tag: str, msg: str) -> None:
    print(f"[{tag}] {msg}", flush=True)


def die(msg: str, code: int = 1):
    log("error", msg)
    sys.exit(code)


TOOL_NAME = Path(__file__).resolve().parent.parent.name
SYMLINK_TARGET = Path.home() / ".local" / "bin" / TOOL_NAME
CLAUDE_COMMAND_TARGET = Path.home() / ".claude" / "commands" / f"{TOOL_NAME}.md"


def _command_source() -> Path:
    return Path(__file__).resolve().parent.parent / "commands" / f"{TOOL_NAME}.md"


# ---------- the workflow ----------

PROJECTS_DIR = Path.home() / ".claude" / "projects"
DEFAULT_TOOLS = {"Bash", "Edit", "Write", "NotebookEdit"}
WIDTH = 160
HOME_PREFIX = re.sub(r"[^A-Za-z0-9]", "-", str(Path.home())) + "-"


def _project_label(project_dir: Path) -> str:
    name = project_dir.name
    return name[len(HOME_PREFIX):] if name.startswith(HOME_PREFIX) else name


def _transcripts(project: str | None, subagents: bool):
    """Yield (project_dir, file, session_id, is_subagent)."""
    if not PROJECTS_DIR.is_dir():
        return
    for proj in sorted(p for p in PROJECTS_DIR.iterdir() if p.is_dir()):
        if project and project not in proj.name:
            continue
        for f in proj.glob("*.jsonl"):
            yield proj, f, f.stem, False
        if subagents:
            for f in proj.glob("*/subagents/*.jsonl"):
                yield proj, f, f.parent.parent.name, True


def _parse_ts(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone()
    except ValueError:
        return None


def _summary(use: dict) -> str:
    inp = use.get("input") or {}
    if use.get("name") == "Bash":
        text = inp.get("command", "")
    elif "file_path" in inp or "notebook_path" in inp:
        text = inp.get("file_path") or inp.get("notebook_path")
    else:
        text = next((v for v in inp.values() if isinstance(v, str)), "")
    text = str(text).replace(str(Path.home()), "~")
    return " ⏎ ".join(line.strip() for line in text.splitlines() if line.strip())


def _read_actions(path: Path, tools: set[str] | None):
    """Return (actions, bad_lines, first_prompt). Each action is (dt, name, summary, is_error)."""
    uses, errors, bad, prompt = [], {}, 0, None
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                bad += 1  # partial last line of a live session, etc.
                continue
            msg = d.get("message")
            if not isinstance(msg, dict):
                continue
            content = msg.get("content")
            if d.get("type") == "user" and prompt is None and isinstance(content, str) \
                    and not content.lstrip().startswith("<"):  # skip command/system wrappers
                prompt = content
            if not isinstance(content, list):
                continue
            for c in content:
                if not isinstance(c, dict):
                    continue
                if d.get("type") == "assistant" and c.get("type") == "tool_use":
                    if tools is None or c.get("name") in tools:
                        uses.append((_parse_ts(d.get("timestamp")), c))
                elif d.get("type") == "user" and c.get("type") == "tool_result":
                    errors[c.get("tool_use_id")] = bool(c.get("is_error"))
                elif d.get("type") == "user" and prompt is None and c.get("type") == "text" \
                        and not c.get("text", "").lstrip().startswith("<"):
                    prompt = c.get("text")
    actions = [(dt, c.get("name", "?"), _summary(c), errors.get(c.get("id"))) for dt, c in uses if dt]
    return actions, bad, prompt


def _resolve_session(target: str | None, project: str | None, subagents: bool):
    """Return the list of transcript tuples belonging to one session."""
    if not target:
        die("session needs an id, prefix, 'current' or 'last'", 2)
    files = list(_transcripts(project, subagents))
    if target == "current":
        target = os.environ.get("CLAUDE_CODE_SESSION_ID") or die(
            "CLAUDE_CODE_SESSION_ID not set — only works inside Claude Code; use 'last' or an id")
    elif target == "last":
        proj = PROJECTS_DIR / re.sub(r"[^A-Za-z0-9]", "-", str(Path.cwd()))
        mains = sorted(proj.glob("*.jsonl"), key=lambda f: f.stat().st_mtime)
        if not mains:
            die(f"no sessions for this directory ({proj})")
        target = mains[-1].stem
    ids = sorted({sid for _, _, sid, _ in files if sid.startswith(target)})
    if not ids:
        die(f"no session matches '{target}'")
    if len(ids) > 1:
        die(f"'{target}' is ambiguous: {', '.join(i[:12] for i in ids[:8])}")
    return [t for t in files if t[2] == ids[0]]


def cmd_actions(args, files) -> int:
    tools = None if args.tools == "all" else set(args.tools.split(","))
    since = date.fromisoformat(args.since) if args.since else None
    only = date.fromisoformat(args.date) if args.date else None
    floor = only or since
    rows, sessions, bad = [], set(), 0
    for proj, f, sid, sub in files:
        if floor and date.fromtimestamp(f.stat().st_mtime) < floor:
            continue  # file untouched since before the window
        actions, nbad, _ = _read_actions(f, tools)
        bad += nbad
        for dt, name, text, err in actions:
            d = dt.date()
            if (only and d != only) or (since and d < since):
                continue
            rows.append((dt, _project_label(proj), sid[:8] + ("[sub]" if sub else ""), name, err, text))
            sessions.add(sid)
    rows.sort(key=lambda r: r[0])
    for dt, proj, sid, name, err, text in rows:
        mark = "·" if err is None else ("✗" if err else "✓")
        if not args.full and len(text) > WIDTH:
            text = text[: WIDTH - 1] + "…"
        print(f"{dt:%Y-%m-%d %H:%M:%S}  {proj}  {sid}  {name:<6} {mark}  {text}")
    if bad:
        log("notice", f"skipped {bad} unparsable line(s)")
    if not rows:
        log("info", "no actions")
        return 0
    errs = sum(1 for r in rows if r[4])
    log("ok", f"{len(rows)} actions in {len(sessions)} session(s) ({errs} errors)")
    return 0


def cmd_sessions(args) -> int:
    try:
        n = int(args.target or 10)
    except ValueError:
        die(f"sessions takes a number, got '{args.target}'", 2)
    mains = [t for t in _transcripts(args.project, False)]
    mains.sort(key=lambda t: t[1].stat().st_mtime, reverse=True)
    for proj, f, sid, _ in mains[:n]:
        actions, _, prompt = _read_actions(f, DEFAULT_TOOLS)
        start = datetime.fromtimestamp(f.stat().st_mtime).astimezone()
        prompt = " ".join((prompt or "").split())[:60]
        print(f"{sid}  {start:%Y-%m-%d %H:%M}  {_project_label(proj)}  {len(actions):>4} actions  {prompt}")
    return 0


def cmd_run(args) -> int:
    subagents = not args.no_subagents
    if args.action == "sessions":
        return cmd_sessions(args)
    if args.action == "session":
        return cmd_actions(args, _resolve_session(args.target, args.project, subagents))
    if not args.date and not args.since:
        args.date = date.today().isoformat()
    return cmd_actions(args, list(_transcripts(args.project, subagents)))


# ---------- install / uninstall ----------

def cmd_install() -> int:
    script_path = Path(__file__).resolve()
    mode = script_path.stat().st_mode
    if not (mode & 0o111):
        script_path.chmod(mode | 0o755)
        log("ok", f"made script executable: {script_path}")
    else:
        log("skip", f"script already executable: {script_path}")
    _install_bin_symlink(script_path)
    _install_claude_command()
    return _install_check_path()


def _install_bin_symlink(script_path: Path) -> None:
    SYMLINK_TARGET.parent.mkdir(parents=True, exist_ok=True)
    if SYMLINK_TARGET.is_symlink():
        current = SYMLINK_TARGET.resolve()
        if current == script_path:
            log("skip", f"bin symlink already correct: {SYMLINK_TARGET} -> {script_path}")
            return
        log("info", f"replacing existing bin symlink ({SYMLINK_TARGET} -> {current})")
        SYMLINK_TARGET.unlink()
    elif SYMLINK_TARGET.exists():
        die(f"{SYMLINK_TARGET} exists and is not a symlink — refusing to overwrite")
    SYMLINK_TARGET.symlink_to(script_path)
    log("ok", f"bin symlink created: {SYMLINK_TARGET} -> {script_path}")


def _install_claude_command() -> None:
    source = _command_source()
    if not source.exists():
        log("notice", f"slash command source not found at {source} — skipping Claude integration")
        return
    CLAUDE_COMMAND_TARGET.parent.mkdir(parents=True, exist_ok=True)
    if CLAUDE_COMMAND_TARGET.is_symlink():
        current = CLAUDE_COMMAND_TARGET.resolve()
        if current == source:
            log("skip", f"slash command symlink already correct: {CLAUDE_COMMAND_TARGET} -> {source}")
            return
        log("info", f"replacing existing slash command symlink ({CLAUDE_COMMAND_TARGET} -> {current})")
        CLAUDE_COMMAND_TARGET.unlink()
    elif CLAUDE_COMMAND_TARGET.exists():
        die(f"{CLAUDE_COMMAND_TARGET} exists and is not a symlink — refusing to overwrite")
    CLAUDE_COMMAND_TARGET.symlink_to(source)
    log("ok", f"slash command symlink created: {CLAUDE_COMMAND_TARGET} -> {source}")


def _install_check_path() -> int:
    on_path = shutil.which(TOOL_NAME)
    if on_path:
        log("ok", f"{TOOL_NAME} on PATH: {on_path}")
        return 0
    log("notice", f"{SYMLINK_TARGET.parent} is not on PATH — add this to your shell rc:")
    log("notice", f'  export PATH="{SYMLINK_TARGET.parent}:$PATH"')
    return 0


def cmd_uninstall() -> int:
    script_path = Path(__file__).resolve()
    _uninstall_bin_symlink()
    _uninstall_claude_command()
    log("info", f"to reinstall: python3 {script_path} install")
    return 0


def _uninstall_bin_symlink() -> None:
    if not SYMLINK_TARGET.is_symlink() and not SYMLINK_TARGET.exists():
        log("info", f"no bin symlink at {SYMLINK_TARGET} to remove")
        return
    if not SYMLINK_TARGET.is_symlink():
        die(f"{SYMLINK_TARGET} exists but is not a symlink — refusing to remove")
    target = SYMLINK_TARGET.resolve()
    SYMLINK_TARGET.unlink()
    log("ok", f"removed bin symlink: {SYMLINK_TARGET} (was -> {target})")


def _uninstall_claude_command() -> None:
    if not CLAUDE_COMMAND_TARGET.is_symlink() and not CLAUDE_COMMAND_TARGET.exists():
        log("info", f"no slash command symlink at {CLAUDE_COMMAND_TARGET} to remove")
        return
    if not CLAUDE_COMMAND_TARGET.is_symlink():
        die(f"{CLAUDE_COMMAND_TARGET} exists but is not a symlink — refusing to remove")
    target = CLAUDE_COMMAND_TARGET.resolve()
    CLAUDE_COMMAND_TARGET.unlink()
    log("ok", f"removed slash command symlink: {CLAUDE_COMMAND_TARGET} (was -> {target})")


# ---------- entry point ----------

def main() -> int:
    parser = argparse.ArgumentParser(
        prog=TOOL_NAME,
        description="claude-audit — list every action Claude Code took, from the session transcripts.",
    )
    parser.add_argument(
        "action",
        nargs="?",
        default="today",
        choices=["today", "run", "session", "sessions", "install", "uninstall"],
        help="today (default; run = alias), session <id>, sessions [N], install/uninstall = manage symlinks",
    )
    parser.add_argument("target", nargs="?", help="session id/prefix/current/last, or N for sessions")
    parser.add_argument("--tools", default=",".join(sorted(DEFAULT_TOOLS)),
                        help="comma list of tool names, or 'all' (default: %(default)s)")
    parser.add_argument("--project", help="only project dirs containing this substring")
    window = parser.add_mutually_exclusive_group()
    window.add_argument("--date", help="only this local date, YYYY-MM-DD")
    window.add_argument("--since", help="from this local date on, YYYY-MM-DD")
    parser.add_argument("--full", action="store_true", help=f"don't truncate at {WIDTH} chars")
    parser.add_argument("--no-subagents", action="store_true", help="skip subagents/*.jsonl")
    args = parser.parse_args()
    for value in (args.date, args.since):
        if value:
            try:
                date.fromisoformat(value)
            except ValueError:
                parser.error(f"bad date '{value}', want YYYY-MM-DD")
    if args.action == "install":
        return cmd_install()
    if args.action == "uninstall":
        return cmd_uninstall()
    return cmd_run(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        log("error", "interrupted")
        sys.exit(130)
