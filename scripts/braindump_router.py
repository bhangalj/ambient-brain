#!/usr/bin/env python3
"""Route a dictated brain-dump into the right place(s) in the vault.

Reads text from a file arg or stdin, asks Claude to split it into typed items
and destinations, then applies them: actions -> inbox, project updates ->
project note, feedback -> feedback log, notes -> daily note, people -> people note.

Usage:
    echo "spent the morning on the billing migration, told Priya it looks good,
          need to follow up with legal about the DPA" | python scripts/braindump_router.py
    python scripts/braindump_router.py note.txt
"""
from __future__ import annotations
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import config, llm, vault  # noqa: E402

SYSTEM = (
    "You triage a person's work brain-dump into structured items for their Obsidian "
    "vault. Only use information present in the dump. Prefer existing project names."
)

PROMPT = """Existing projects: {projects}

Split this dump into items. Return JSON:
{{ "items": [
   {{ "kind": "action|project_update|feedback|note|person",
      "text": "...",
      "target": "project slug, person name, or null" }}
] }}

DUMP:
{dump}"""


def apply(item: dict, touched: set[str] | None = None) -> str:
    """Apply one routed item; records touched project slugs into `touched`."""
    kind = item.get("kind")
    text = item.get("text", "").strip()
    target = item.get("target")
    if not text:
        return "skip"
    if kind == "action":
        vault.add_action(text, "braindump", {})
        return "→ inbox"
    if kind == "project_update" and target:
        slug = vault.ensure_project(target)  # real frontmatter + §4 sections
        if touched is not None:
            touched.add(slug)
        vault.append_section(
            vault.VAULT / "02-projects" / slug / "_project.md",
            "Log", [f"- {datetime.now():%Y-%m-%d} {text}"])
        return f"→ project {target}"
    if kind == "feedback":
        vault.append_section(
            vault.VAULT / "05-feedback" / f"{datetime.now().year}.md",
            "Brain-dump", [f"- {text}"])
        return "→ feedback"
    if kind == "person" and target:
        vault.append_section(
            vault.VAULT / "04-people" / f"{vault.slugify(target)}.md",
            "Notes", [f"- {datetime.now():%Y-%m-%d} {text}"])
        return f"→ person {target}"
    # default: daily note
    vault.append_section(
        vault.VAULT / "01-daily" / f"{datetime.now():%Y-%m-%d}.md",
        "Notes", [f"- {text}"])
    return "→ daily"


def main() -> None:
    dump = (Path(sys.argv[1]).read_text(encoding="utf-8")
            if len(sys.argv) > 1 else sys.stdin.read())
    if not dump.strip():
        raise SystemExit("Nothing to route (empty input).")
    projects = sorted(p.name for p in (vault.VAULT / "02-projects").iterdir() if p.is_dir())
    model = config.load().get("llm", {}).get("model", "claude-sonnet-5")
    data = llm.complete_json(SYSTEM, PROMPT.format(projects=", ".join(projects) or "none",
                                                   dump=dump), model=model)
    touched: set[str] = set()
    applied = 0
    for item in data.get("items", []):
        try:  # one malformed item must not strand earlier writes with stale digests
            result = apply(item, touched)
        except Exception as e:  # noqa: BLE001
            print(f"{'?':15} ! skipped malformed item: {e}")
            continue
        kind = item.get("kind", "?") if isinstance(item, dict) else "?"
        print(f"{kind:15} {result}")
        if result != "skip":
            applied += 1
    if applied:  # digest invariant (§6): every write leaves digests + dashboard current
        for slug in sorted(touched):
            vault.refresh_digest(slug)
        vault.regenerate_dashboard()


if __name__ == "__main__":
    main()
