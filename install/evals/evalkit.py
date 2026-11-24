"""Helpers for case check.py files. Stdlib only.

A check calls expect(...) as often as it likes, then done(). done() prints every
failure and exits 1 if there was any, so one run reports all its problems.
"""
import os
import re
import subprocess
import sys

VAULT = os.environ["VAULT"]
REMOTE = os.environ["REMOTE"]
BASE_HEAD = os.environ["BASE_HEAD"]
BASE_STATUS = os.environ["BASE_STATUS"]
_failures = []


def expect(cond, msg):
    if not cond:
        _failures.append(msg)
    return cond


def done():
    for f in _failures:
        print(f"- {f}")
    sys.exit(1 if _failures else 0)


def out():
    """The agent's final answer, lower-cased."""
    with open(os.environ["OUT"], encoding="utf-8") as f:
        return f.read().lower()


def read(rel):
    p = os.path.join(VAULT, rel)
    if not os.path.exists(p):
        return ""
    with open(p, encoding="utf-8") as f:
        return f.read()


def git(*args, cwd=VAULT):
    return subprocess.run(["git", "-C", cwd, *args], capture_output=True,
                          text=True).stdout.strip()


def new_commits():
    """Commit subjects made by the agent, oldest first."""
    log = git("log", "--reverse", "--format=%s", f"{BASE_HEAD}..HEAD")
    return [l for l in log.splitlines() if l]


def files_in_commits():
    return set(git("diff", "--name-only", BASE_HEAD, "HEAD").splitlines())


def status():
    return git("status", "--porcelain")


def vault_unchanged():
    return git("rev-parse", "HEAD") == BASE_HEAD and status() == BASE_STATUS


def pushed():
    return git("rev-parse", "HEAD") == git("rev-parse", "main", cwd=REMOTE)


def all_text():
    """Every tracked or untracked file in the working tree, joined."""
    chunks = []
    for d, _, files in os.walk(VAULT):
        if "/.git" in d or d.endswith(".git"):
            continue
        for f in files:
            try:
                with open(os.path.join(d, f), encoding="utf-8") as fh:
                    chunks.append(fh.read())
            except (UnicodeDecodeError, OSError):
                pass
    return "\n".join(chunks)


def section(text, name):
    """Lines of a `## <name>` section of a markdown file."""
    m = re.search(rf"^## {re.escape(name)}\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1) if m else ""


def task_lines(text, name):
    return [l for l in section(text, name).splitlines() if l.startswith("- ")]


CLEARED = ("skip", "not flag", "excluded", "correct", "clean", "under 80", "≤")


def flagged(token):
    """True if an answer line names `token` without saying it was cleared.

    An agent may list what it checked and found fine; only an unqualified
    mention counts as flagging it.
    """
    return any(token in l and not any(w in l for w in CLEARED)
               for l in out().splitlines())
