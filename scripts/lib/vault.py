"""Helpers for writing well-formed Obsidian notes: YAML frontmatter, idempotent
upserts, and appends to the shared action inbox.
"""
from __future__ import annotations
import re
from datetime import datetime, timezone
from pathlib import Path

import yaml

VAULT = Path(__file__).resolve().parents[2]
ACTIONS = VAULT / "00-inbox" / "actions.md"


def slugify(text: str, max_len: int = 60) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    text = re.sub(r"[\s_-]+", "-", text)
    return text[:max_len].strip("-") or "untitled"


def dump_frontmatter(meta: dict) -> str:
    fm = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True).strip()
    return f"---\n{fm}\n---\n"


def write_note(path: Path, meta: dict, body: str, overwrite: bool = True) -> Path:
    """Create/replace a note. Idempotent by path — safe to re-run syncs."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        return path
    path.write_text(dump_frontmatter(meta) + "\n" + body.strip() + "\n")
    return path


def append_section(path: Path, heading: str, lines: list[str]) -> None:
    """Append bullet lines under a heading, creating the file/heading if absent."""
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text() if path.exists() else ""
    if heading not in existing:
        existing += f"\n\n## {heading}\n"
    block = "\n".join(lines)
    # insert right after the heading line
    out = existing.replace(f"## {heading}\n", f"## {heading}\n{block}\n", 1)
    path.write_text(out)


def add_action(text: str, source: str, meta: dict | None = None) -> None:
    """Append a todo to the action inbox as a markdown checkbox.

    `meta` (e.g. slack channel/ts/permalink) is embedded as an inline HTML
    comment so the update loop (close_actions.py) can act on the source message.
    """
    ACTIONS.parent.mkdir(parents=True, exist_ok=True)
    if not ACTIONS.exists():
        ACTIONS.write_text(
            "---\ntype: inbox\n---\n\n# Action Inbox\n\n"
            "Auto-populated from Slack/email/meetings. Tick a box to mark done; "
            "`close_actions.py` will react in Slack and archive it.\n\n"
            "## Open\n"
        )
    tag = f"<!-- src:{source} " + " ".join(f"{k}={v}" for k, v in (meta or {}).items()) + " -->"
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    line = f"- [ ] {text}  (from {source}, {stamp}) {tag}"
    content = ACTIONS.read_text()
    content = content.replace("## Open\n", f"## Open\n{line}\n", 1)
    ACTIONS.write_text(content)
