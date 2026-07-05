#!/usr/bin/env python3
"""Claude Code Stop/SessionEnd hook (§5, §12).

Runs at the end of every turn: if the vault working tree changed, one batched
add -> commit -> pull --rebase -> push via lib.gitsync. Never per-file commits,
no transcript ingest (that moved to CI, §8). Receives hook JSON on stdin but
tolerates its absence. ALWAYS exits 0 — a failing hook must never block the
user's Claude Code session.

Wire it up in .claude/settings.json (see .claude/settings.example.json).
"""
from __future__ import annotations
import subprocess
import sys
from datetime import datetime
from pathlib import Path

VAULT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(VAULT / "scripts"))


def main() -> int:
    try:  # consume hook payload; unused
        if not sys.stdin.isatty():
            sys.stdin.read()
    except Exception:  # noqa: BLE001
        pass
    try:
        status = subprocess.run(["git", "status", "--porcelain", "--branch"],
                                cwd=str(VAULT), capture_output=True, text=True,
                                encoding="utf-8", errors="replace")
        lines = status.stdout.splitlines()
        dirty = any(not ln.startswith("##") for ln in lines)
        ahead = bool(lines) and "[ahead" in lines[0]  # stranded unpushed commit
        if status.returncode == 0 and not dirty and not ahead:
            print("nothing-to-capture")
            return 0
        from lib import gitsync  # noqa: PLC0415 — import after sys.path fix
        result = gitsync.sync_repo(
            f"session capture {datetime.now():%Y-%m-%d %H:%M}", cwd=VAULT)
        print(f"session-capture: {result}")
    except Exception as e:  # noqa: BLE001
        print(f"session-capture: error ({e})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
