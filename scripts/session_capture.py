#!/usr/bin/env python3
"""Claude Code SessionEnd hook.

Runs when a Claude Code session closes: it drains any pending transcripts/
brain-dumps, closes completed actions, then commits + pushes the vault so the
brain is never stale. Receives hook JSON on stdin (session_id, transcript_path,
reason) but doesn't require it.

Wire it up in .claude/settings.json (see .claude/settings.example.json).
"""
from __future__ import annotations
import subprocess
import sys
from datetime import datetime
from pathlib import Path

VAULT = Path(__file__).resolve().parents[1]


def run(cmd: list[str], **kw) -> int:
    return subprocess.run(cmd, cwd=VAULT, **kw).returncode


def maybe(script: str) -> None:
    try:
        run([sys.executable, f"scripts/{script}"], check=False)
    except Exception as e:  # noqa: BLE001
        print(f"  ! {script}: {e}", file=sys.stderr)


def main() -> None:
    _ = sys.stdin.read()  # consume hook payload; unused for now
    maybe("ingest_transcript.py")
    maybe("close_actions.py")
    # commit + push if anything changed
    changed = subprocess.run(["git", "status", "--porcelain"], cwd=VAULT,
                             capture_output=True, text=True).stdout.strip()
    if changed:
        run(["git", "add", "-A"])
        run(["git", "commit", "-q", "-m",
             f"session capture {datetime.now():%Y-%m-%d %H:%M}"])
        run(["git", "push", "-q"])
        print("Vault committed + pushed.")
    else:
        print("Nothing to capture.")


if __name__ == "__main__":
    main()
