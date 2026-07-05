"""Sync-state: per-source cursors + a bounded seen-id set for idempotent syncs.

State lives at 99-meta/sync-state.json so re-runs never duplicate notes.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

VAULT = Path(__file__).resolve().parents[2]
STATE_PATH = VAULT / "99-meta" / "sync-state.json"
_MAX_SEEN = 5000  # keep the most recent N ids per source


def load() -> dict[str, Any]:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text())
    return {"cursors": {}, "seen": {}}


def save(state: dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True))


def get_cursor(state: dict, source: str, default: str | None = None) -> str | None:
    return state.get("cursors", {}).get(source, default)


def set_cursor(state: dict, source: str, value: str) -> None:
    state.setdefault("cursors", {})[source] = value


def seen(state: dict, source: str, item_id: str) -> bool:
    return item_id in state.get("seen", {}).get(source, [])


def mark_seen(state: dict, source: str, item_id: str) -> None:
    bucket = state.setdefault("seen", {}).setdefault(source, [])
    if item_id not in bucket:
        bucket.append(item_id)
    if len(bucket) > _MAX_SEEN:
        del bucket[: len(bucket) - _MAX_SEEN]
