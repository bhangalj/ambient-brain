"""Transcript-source adapters.

An adapter turns one provider's webhook payload into the normalized dict the
vault ingester understands. Add a provider = add one file here and register it.

Normalized shape:
{
  "provider": "fathom",
  "external_id": "unique id for dedup / filename",
  "title": "...",
  "date": "YYYY-MM-DD" | None,
  "attendees": ["Name <email>", ...],
  "segments": [{"speaker": "...", "text": "...", "ts": "00:00:15"}, ...],
  "summary": "..." | None,          # provider-supplied, optional
  "action_items": [{"owner": "...", "task": "..."}],  # provider-supplied, optional
  "url": "https://..." | None,
}
"""
from __future__ import annotations
from typing import Callable

_REGISTRY: dict[str, Callable[[dict], dict]] = {}


def register(name: str):
    def deco(fn: Callable[[dict], dict]):
        _REGISTRY[name] = fn
        return fn
    return deco


def normalize(provider: str, payload: dict) -> dict:
    if provider not in _REGISTRY:
        raise KeyError(f"No adapter registered for '{provider}'. Have: {list(_REGISTRY)}")
    return _REGISTRY[provider](payload)
