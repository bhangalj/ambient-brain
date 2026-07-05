"""Load config.yaml (knobs) + environment (secrets)."""
from __future__ import annotations
import os
from pathlib import Path

import yaml

VAULT = Path(__file__).resolve().parents[2]
CONFIG_PATH = VAULT / "config.yaml"


def load() -> dict:
    if not CONFIG_PATH.exists():
        raise SystemExit("config.yaml not found — copy config.example.yaml first.")
    return yaml.safe_load(CONFIG_PATH.read_text()) or {}


def env(key: str, required: bool = True) -> str | None:
    val = os.environ.get(key)
    if required and not val:
        raise SystemExit(f"Missing required env var: {key}")
    return val
