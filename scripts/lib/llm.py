"""Thin Anthropic wrapper used by transcript cleaning + brain-dump routing.

Env: ANTHROPIC_API_KEY. Model is configurable via config.yaml -> llm.model.
"""
from __future__ import annotations
import json
import os

import requests

API = "https://api.anthropic.com/v1/messages"


def complete(system: str, prompt: str, model: str = "claude-sonnet-5",
             max_tokens: int = 4000) -> str:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise SystemExit("Missing ANTHROPIC_API_KEY")
    r = requests.post(API, headers={
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }, json={
        "model": model,
        "max_tokens": max_tokens,
        "system": system,
        "messages": [{"role": "user", "content": prompt}],
    }, timeout=120)
    r.raise_for_status()
    blocks = r.json().get("content", [])
    return "".join(b.get("text", "") for b in blocks if b.get("type") == "text")


def complete_json(system: str, prompt: str, **kw) -> dict:
    """Force-parse a JSON object from the model, tolerating code fences."""
    raw = complete(system + "\nRespond with ONLY a JSON object, no prose, no fences.",
                   prompt, **kw)
    raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(raw)
