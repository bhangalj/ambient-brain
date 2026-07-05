#!/usr/bin/env python3
"""Digest lint (DESIGN §13): warn when a project's `digest_updated` frontmatter
stamp is missing or older than the project's latest git activity.

Report-only in P1 — prints WARN/OK lines and always exits 0.
"""
from __future__ import annotations
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import vault  # noqa: E402

VAULT = vault.VAULT
PROJECTS = VAULT / "02-projects"


def split_frontmatter(text: str) -> tuple[dict, str]:
    """Return (frontmatter dict, body). Defers to lib/vault.py if it grows one."""
    if hasattr(vault, "split_frontmatter"):
        return vault.split_frontmatter(text)
    if text.startswith("---\n"):
        head, _, body = text[4:].partition("\n---\n")
        try:
            return yaml.safe_load(head) or {}, body
        except yaml.YAMLError:
            pass
    return {}, text


def last_activity(slug: str) -> str:
    """Latest commit date (YYYY-MM-DD) touching the project folder, '' if none."""
    out = subprocess.run(
        ["git", "log", "-1", "--format=%cs", "--", f"02-projects/{slug}"],
        cwd=VAULT, capture_output=True, text=True, encoding="utf-8",
    )
    return out.stdout.strip()


def _stale(stamp: str, active: str) -> bool:
    """1-day grace: stamps are UTC dates, git %cs is the committer's local date."""
    try:
        return date.fromisoformat(active) - date.fromisoformat(stamp) > timedelta(days=1)
    except ValueError:
        return stamp < active  # unparseable — fall back to strict compare


def main() -> None:
    warns = 0
    notes = sorted(PROJECTS.glob("*/_project.md"))
    for note in notes:
        slug = note.parent.name
        meta, _ = split_frontmatter(note.read_text(encoding="utf-8"))
        stamp = str(meta.get("digest_updated") or "")[:10]
        active = last_activity(slug)
        if not stamp:
            print(f"WARN {slug}: no digest_updated stamp (last activity {active or 'unknown'})")
            warns += 1
        elif active and _stale(stamp, active):
            print(f"WARN {slug}: digest_updated {stamp} older than last activity {active}")
            warns += 1
    if warns:
        print(f"digest lint: {warns}/{len(notes)} project(s) stale (report-only, not failing)")
    else:
        print(f"digest lint: OK - {len(notes)} project(s) checked, all digests current")
    sys.exit(0)


if __name__ == "__main__":
    main()
