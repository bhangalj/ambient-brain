"""Shared git convergence for every vault writer (§5): one batched
add -> commit -> pull --rebase -> push, with a single rebase-retry on rejection.
Never raises; never leaves the repo mid-rebase.
"""
from __future__ import annotations
import subprocess
from pathlib import Path

VAULT = Path(__file__).resolve().parents[2]


def _git(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True,
                          text=True, encoding="utf-8", errors="replace")


def _why(proc: subprocess.CompletedProcess) -> str:
    return " ".join((proc.stderr or proc.stdout or "unknown").split())[:200]


def sync_repo(message: str, cwd: Path = VAULT) -> str:
    """Batched commit + rebase + push. Returns a short status string."""
    try:
        git_dir = Path(cwd) / ".git"
        if ((git_dir / "rebase-merge").exists() or (git_dir / "rebase-apply").exists()
                or (git_dir / "MERGE_HEAD").exists()):
            return "skipped: repo mid-rebase/merge — resolve manually"

        _git(["add", "-A"], cwd)
        committed = False
        if _git(["diff", "--cached", "--quiet"], cwd).returncode != 0:
            c = _git(["commit", "-q", "-m", message], cwd)
            if c.returncode != 0:
                return f"commit-failed: {_why(c)}"
            committed = True

        pull = _git(["pull", "--rebase", "-q"], cwd)
        if pull.returncode != 0:
            _git(["rebase", "--abort"], cwd)  # no-op if no rebase in progress
            state = "committed-not-pushed" if committed else "not-pushed"
            return f"{state}: pull --rebase failed ({_why(pull)})"

        push = _git(["push", "-q"], cwd)
        if push.returncode != 0:
            # rejected (someone pushed since our pull): rebase once more, retry
            pull = _git(["pull", "--rebase", "-q"], cwd)
            if pull.returncode != 0:
                _git(["rebase", "--abort"], cwd)
                state = "committed-not-pushed" if committed else "not-pushed"
                return f"{state}: rebase-retry failed ({_why(pull)})"
            push = _git(["push", "-q"], cwd)
            if push.returncode != 0:
                state = "committed-not-pushed" if committed else "not-pushed"
                return f"{state}: push rejected twice ({_why(push)})"

        return "pushed" if committed else "nothing-to-commit"
    except Exception as e:  # noqa: BLE001 — a sync failure must never kill a writer
        return f"error: {e}"
