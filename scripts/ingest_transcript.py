#!/usr/bin/env python3
"""Ingest meeting transcripts dropped into 00-inbox/transcripts/.

Source-agnostic: point Granola/Otter/Fireflies/Fathom/Zoom exports (or a webhook)
at that folder. Accepts .txt .md .vtt .srt .json. For each new file it:
  1. normalises to plain text (strips VTT/SRT timing),
  2. asks Claude to produce a clean structured note (summary, decisions, actions,
     attendees) with [[wikilinks]] to people/projects — the "LLM wiki" step,
  3. writes it to 03-meetings/<date>-<slug>.md,
  4. pushes action items into the inbox,
  5. moves the raw file to 03-meetings/_raw/.

Run on a fast local loop (cron / fswatch / SessionEnd hook), not weekly.
"""
from __future__ import annotations
import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import config, llm, vault  # noqa: E402

INBOX = vault.VAULT / "00-inbox" / "transcripts"
RAW = vault.VAULT / "03-meetings" / "_raw"

SYSTEM = (
    "You clean raw meeting transcripts into a structured Obsidian note. Be faithful; "
    "do not invent facts. Use [[wikilinks]] for people and project names you can "
    "identify. Keep the cleaned transcript readable but complete."
)

TEMPLATE = """Transcript below. Return JSON with keys:
  title (short), date (YYYY-MM-DD or null), attendees (list of names),
  projects (list of project names mentioned), summary (3-6 sentences),
  decisions (list), actions (list of {{owner, task}}), cleaned (the tidied transcript md).

TRANSCRIPT:
{body}"""


def to_text(path: Path) -> str:
    raw = path.read_text(errors="ignore")
    if path.suffix == ".json":
        try:
            data = json.loads(raw)
            # normalized webhook payload (from webhook/adapters) — keep provider
            # summary/actions/attendees so the LLM doesn't discard them.
            hints = ""
            if isinstance(data, dict) and data.get("provider"):
                if data.get("attendees"):
                    hints += "ATTENDEES: " + ", ".join(data["attendees"]) + "\n"
                if data.get("summary"):
                    hints += "PROVIDER SUMMARY:\n" + str(data["summary"]) + "\n"
                if data.get("action_items"):
                    hints += "PROVIDER ACTION ITEMS: " + json.dumps(data["action_items"]) + "\n"
            # common shapes: list of {speaker,text} or {segments:[...]}
            segs = data if isinstance(data, list) else data.get("segments", [])
            body = "\n".join(
                f"{s.get('speaker','')}: {s.get('text', s.get('content',''))}".strip(": ")
                for s in segs
            )
            return (hints + "\n" + body).strip() or raw
        except Exception:
            return raw
    if path.suffix in (".vtt", ".srt"):
        lines = []
        for ln in raw.splitlines():
            if "-->" in ln or ln.strip().isdigit() or ln.strip().upper() == "WEBVTT":
                continue
            if ln.strip():
                lines.append(ln.strip())
        return "\n".join(lines)
    return raw


def process(path: Path, model: str) -> None:
    body = to_text(path)[:120_000]
    data = llm.complete_json(SYSTEM, TEMPLATE.format(body=body), model=model)
    date = data.get("date") or datetime.now().strftime("%Y-%m-%d")
    slug = vault.slugify(data.get("title", path.stem))
    meta = {
        "type": "meeting", "source": "transcript",
        "title": data.get("title"), "date": date,
        "attendees": [f"[[{n}]]" for n in data.get("attendees", [])],
        "projects": [f"[[{vault.slugify(p)}/_project|{p}]]" for p in data.get("projects", [])],
    }
    parts = [f"# {data.get('title','Meeting')}", "", "## Summary", data.get("summary", "")]
    if data.get("decisions"):
        parts += ["", "## Decisions"] + [f"- {d}" for d in data["decisions"]]
    if data.get("actions"):
        parts += ["", "## Action items"]
        for a in data["actions"]:
            owner = a.get("owner", "")
            parts.append(f"- [ ] {a.get('task','')}" + (f" — {owner}" if owner else ""))
            vault.add_action(f"{a.get('task','')}", "meeting",
                             {"meeting": f"{date}-{slug}", "owner": owner})
    parts += ["", "## Transcript", "", data.get("cleaned", body)]

    vault.write_note(vault.VAULT / "03-meetings" / f"{date}-{slug}.md", meta,
                     "\n".join(parts))
    RAW.mkdir(parents=True, exist_ok=True)
    path.rename(RAW / path.name)
    print(f"  ✓ {date}-{slug}.md")


def main() -> None:
    model = config.load().get("llm", {}).get("model", "claude-sonnet-5")
    files = [p for p in INBOX.iterdir()
             if p.is_file() and p.suffix in (".txt", ".md", ".vtt", ".srt", ".json")
             and p.name != ".gitkeep"]
    if not files:
        print("No new transcripts.")
        return
    for p in sorted(files):
        print(f"Processing {p.name} …")
        try:
            process(p, model)
        except Exception as e:  # noqa: BLE001
            print(f"  ! failed: {e}")


if __name__ == "__main__":
    main()
