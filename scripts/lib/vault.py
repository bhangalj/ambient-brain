"""Helpers for writing well-formed Obsidian notes: YAML frontmatter, idempotent
upserts, appends to the shared action inbox, plus the digest invariant (§6)
and DASHBOARD regeneration (§4) that every writer shares.
"""
from __future__ import annotations
import re
from datetime import datetime, timezone
from pathlib import Path

import yaml

VAULT = Path(__file__).resolve().parents[2]
ACTIONS = VAULT / "00-inbox" / "actions.md"
DASHBOARD = VAULT / "DASHBOARD.md"

PROJECT_SECTIONS = ["Current state", "How it works", "Decisions", "Ideas / future", "Log"]


def slugify(text: str, max_len: int = 60) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    text = re.sub(r"[\s_-]+", "-", text)
    return text[:max_len].strip("-") or "untitled"


def dump_frontmatter(meta: dict) -> str:
    fm = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True).strip()
    return f"---\n{fm}\n---\n"


def split_frontmatter(text: str) -> tuple[dict, str]:
    """Parse leading YAML frontmatter -> (meta, body). ({}, text) if absent/broken."""
    m = re.match(r"^---[ \t]*\n(.*?)\n---[ \t]*\n?", text, re.DOTALL)
    if not m:
        return {}, text
    try:
        meta = yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        return {}, text
    if not isinstance(meta, dict):
        return {}, text
    return meta, text[m.end():]


def write_note(path: Path, meta: dict, body: str, overwrite: bool = True) -> Path:
    """Create/replace a note. Idempotent by path — safe to re-run syncs."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        return path
    path.write_text(dump_frontmatter(meta) + "\n" + body.strip() + "\n",
                    encoding="utf-8")
    return path


def append_section(path: Path, heading: str, lines: list[str]) -> None:
    """Append bullet lines under a heading, creating the file/heading if absent."""
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    if existing and not existing.endswith("\n"):
        existing += "\n"
    marker = f"## {heading}"
    pat = re.compile(rf"(?m)^{re.escape(marker)}[ \t]*\n")
    if not pat.search(existing):
        existing += f"\n{marker}\n"
    block = "\n".join(lines)
    # insert right after the heading line (lambda: block may contain backslashes)
    out = pat.sub(lambda _: f"{marker}\n{block}\n", existing, count=1)
    path.write_text(out, encoding="utf-8")


def replace_section(text: str, heading: str, new_body: str) -> str:
    """Replace content between '## <heading>' and the next '## ' (or EOF).

    Appends the section if the heading is absent.
    """
    if text and not text.endswith("\n"):
        text += "\n"
    marker = f"## {heading}"
    body = new_body.strip("\n")
    pat = re.compile(rf"(?ms)^{re.escape(marker)}[ \t]*\n.*?(?=^## |\Z)")
    if pat.search(text):
        return pat.sub(lambda _: f"{marker}\n\n{body}\n\n", text, count=1)
    return text + f"\n{marker}\n\n{body}\n"


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
            "## Open\n",
            encoding="utf-8",
        )
    tag = f"<!-- src:{source} " + " ".join(f"{k}={v}" for k, v in (meta or {}).items()) + " -->"
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    line = f"- [ ] {text}  (from {source}, {stamp}) {tag}"
    content = ACTIONS.read_text(encoding="utf-8")
    content = content.replace("## Open\n", f"## Open\n{line}\n", 1)
    ACTIONS.write_text(content, encoding="utf-8")


def ensure_project(name: str) -> str:
    """Ensure 02-projects/<slug>/_project.md exists (§4 layout); returns the slug."""
    slug = slugify(name)
    path = VAULT / "02-projects" / slug / "_project.md"
    if not path.exists():
        meta = {
            "type": "project",
            "name": name,
            "status": "active",
            "repos": [],
            "people": [],
            "created": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        }
        body = f"# {name}\n\n" + "\n".join(f"## {s}\n" for s in PROJECT_SECTIONS)
        write_note(path, meta, body)
    return slug


# --- digest refresh (§6) -----------------------------------------------------

def _section(text: str, heading: str) -> str:
    """Body of '## <heading>' up to the next '## ' or EOF ('' if absent)."""
    m = re.search(rf"(?ms)^## {re.escape(heading)}[ \t]*\n(.*?)(?=^## |\Z)", text)
    return m.group(1).strip() if m else ""


def _bullets(text: str) -> list[str]:
    return [ln.strip() for ln in text.splitlines() if ln.strip().startswith("- ")]


def _open_tasks(pdir: Path) -> list[dict]:
    """Open tasks (state_type not completed/canceled) from tasks/*.md frontmatter."""
    tasks = []
    tdir = pdir / "tasks"
    if not tdir.is_dir():
        return tasks
    for p in sorted(tdir.glob("*.md")):
        meta, _ = split_frontmatter(p.read_text(encoding="utf-8"))
        if str(meta.get("state_type")) in ("completed", "canceled"):
            continue
        tasks.append({"id": str(meta.get("id") or p.stem),
                      "title": str(meta.get("title") or p.stem),
                      "status": str(meta.get("status") or "open")})
    return tasks


def _recent_meetings(slug: str, limit: int = 5) -> list[str]:
    """Titles of the most recent meeting notes whose frontmatter mentions slug."""
    mdir = VAULT / "03-meetings"
    hits: list[str] = []
    if not mdir.is_dir():
        return hits
    for p in sorted(mdir.glob("*.md"), reverse=True):  # date-prefixed names
        meta, _ = split_frontmatter(p.read_text(encoding="utf-8"))
        mentioned = str(meta.get("projects") or meta.get("project") or "")
        if slug in mentioned:
            hits.append(str(meta.get("title") or p.stem))
        if len(hits) >= limit:
            break
    return hits


def _llm_model() -> str:
    cfg = VAULT / "config.yaml"
    if cfg.exists():
        try:
            data = yaml.safe_load(cfg.read_text(encoding="utf-8")) or {}
            return data.get("llm", {}).get("model", "claude-sonnet-5")
        except Exception:  # noqa: BLE001
            pass
    return "claude-sonnet-5"


def _structural_digest(slug: str, meta: dict, tasks: list[dict], log_lines: list[str],
                       done_lines: list[str], decisions: list[str],
                       meetings: list[str]) -> str:
    """Deterministic fallback digest — no LLM, built from gathered context."""
    out = [f"**{str(meta.get('status', 'active')).capitalize()}** — "
           f"{len(tasks)} open task(s)."]
    if tasks:
        out += ["", "**Open tasks**"]
        out += [f"- [[tasks/{t['id']}|{t['id']}]] {t['title']} ({t['status']})"
                for t in tasks[:5]]
    if decisions:
        out += ["", "**Recent decisions**"] + decisions[-3:]
    if log_lines or done_lines:
        out += ["", "**Recent activity**"] + log_lines[-5:] + done_lines[-5:]
    deeper = [str(r) for r in (meta.get("repos") or [])]
    if (VAULT / "02-projects" / slug / "done.md").exists():
        deeper.append(f"[[{slug}/done|done log]]")
    deeper += [f"[[{m}]]" for m in meetings[:3]]
    if deeper:
        out += ["", "**Deeper:** " + " · ".join(deeper)]
    return "\n".join(out)


def refresh_digest(slug: str) -> bool:
    """Rebuild '## Current state' of 02-projects/<slug>/_project.md (§6).

    Never raises — a digest failure must not kill a sync. Returns False on
    any failure or if the project note doesn't exist.
    """
    try:
        import os
        pdir = VAULT / "02-projects" / slug
        note = pdir / "_project.md"
        if not note.exists():
            return False
        meta, body = split_frontmatter(note.read_text(encoding="utf-8"))
        tasks = _open_tasks(pdir)
        log_lines = _bullets(_section(body, "Log"))[-5:]
        decisions = _bullets(_section(body, "Decisions"))
        done = pdir / "done.md"
        done_lines = []
        if done.exists():
            _, done_body = split_frontmatter(done.read_text(encoding="utf-8"))
            done_lines = _bullets(done_body)[-5:]
        meetings = _recent_meetings(slug)
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        content = None
        if os.environ.get("ANTHROPIC_API_KEY"):
            try:
                from . import llm
                context = "\n\n".join(filter(None, [
                    f"PROJECT: {meta.get('name', slug)} (slug: {slug})",
                    "FRONTMATTER:\n" + yaml.safe_dump(meta, sort_keys=False,
                                                      allow_unicode=True).strip(),
                    "OPEN TASKS:\n" + "\n".join(
                        f"- {t['id']}: {t['title']} ({t['status']})" for t in tasks),
                    "RECENT LOG:\n" + "\n".join(log_lines),
                    "RECENT DONE:\n" + "\n".join(done_lines),
                    "DECISIONS:\n" + "\n".join(decisions),
                    "RECENT MEETINGS:\n" + "\n".join(meetings),
                ]))
                system = (
                    "You maintain the '## Current state' digest of a project note in "
                    "an Obsidian work vault. From the provided context ONLY, write a "
                    "tight digest under 500 tokens: a 1-2 sentence status, then "
                    "'**Recent decisions**', '**Open threads**', and a '**Deeper**' "
                    "line of wikilinks (e.g. [[tasks/ABC-1]]). Markdown bullets, no "
                    "'#' headings, no preamble."
                )
                content = llm.complete(system, context, model=_llm_model(),
                                       max_tokens=700).strip()
            except Exception:  # noqa: BLE001 — LLM failure falls back
                content = None
        if not content:
            content = _structural_digest(slug, meta, tasks, log_lines,
                                         done_lines, decisions, meetings)

        digest = f"*(updated {today} · auto)*\n\n{content}"
        meta["digest_updated"] = today
        new_body = replace_section(body, "Current state", digest)
        note.write_text(dump_frontmatter(meta) + "\n" + new_body.strip() + "\n",
                        encoding="utf-8")
        return True
    except Exception:  # noqa: BLE001
        return False


# --- dashboard regeneration (§4) ----------------------------------------------

def _esc_cell(text: str) -> str:
    return text.replace("|", "\\|")


def regenerate_dashboard() -> None:
    """Full deterministic rewrite of DASHBOARD.md (§4). No LLM."""
    projects = []
    root = VAULT / "02-projects"
    if root.is_dir():
        for pdir in sorted(p for p in root.iterdir() if p.is_dir()):
            note = pdir / "_project.md"
            if not note.exists():
                continue
            meta, body = split_frontmatter(note.read_text(encoding="utf-8"))
            state_line = ""
            for ln in _section(body, "Current state").splitlines():
                ln = ln.strip()
                if ln and not ln.startswith("*("):
                    state_line = ln
                    break
            if len(state_line) > 90:
                state_line = state_line[:89] + "…"
            projects.append({
                "slug": pdir.name,
                "name": str(meta.get("name") or pdir.name),
                "status": str(meta.get("status") or "active"),
                "open": len(_open_tasks(pdir)),
                "digest_updated": str(meta.get("digest_updated") or "—"),
                "state": state_line or "—",
                "ideas": _bullets(_section(body, "Ideas / future")),
            })

    lines = ["> Machine-generated by `scripts/lib/vault.py` — do not hand-edit.",
             "", "# Dashboard", "", "## Projects", ""]
    if not projects:
        lines += ["_No projects yet._", ""]
    else:
        statuses = ["active"] + sorted({p["status"] for p in projects} - {"active"})
        for status in statuses:
            group = [p for p in projects if p["status"] == status]
            if not group:
                continue
            lines += [f"### {status.capitalize()}", "",
                      "| Project | Open tasks | Digest updated | State |",
                      "|---|---|---|---|"]
            for p in group:
                link = f"[[{p['slug']}/_project\\|{_esc_cell(p['name'])}]]"
                lines.append(f"| {link} | {p['open']} | {p['digest_updated']} "
                             f"| {_esc_cell(p['state'])} |")
            lines.append("")

    open_count = 0
    if ACTIONS.exists():
        open_count = sum(1 for ln in ACTIONS.read_text(encoding="utf-8").splitlines()
                         if ln.lstrip().startswith("- [ ]"))
    lines += ["## Open actions", "",
              f"**{open_count}** open — see [[00-inbox/actions|action inbox]].", ""]

    lines += ["## Ideas queue", ""]
    ideas = []
    for p in projects:
        link = f"[[{p['slug']}/_project|{p['name']}]]"
        ideas += [f"- {link}: {idea[2:].strip()}" for idea in p["ideas"]]
    ref = VAULT / "07-reference"
    if ref.is_dir():
        for p in sorted(ref.glob("*.md")):
            meta, _ = split_frontmatter(p.read_text(encoding="utf-8"))
            if str(meta.get("type")) == "idea":
                title = str(meta.get("title") or p.stem)
                ideas.append(f"- [[07-reference/{p.stem}|{title}]]")
    lines += ideas if ideas else ["_No ideas queued._"]

    meta = {"type": "dashboard",
            "updated": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    DASHBOARD.write_text(dump_frontmatter(meta) + "\n" + "\n".join(lines).strip() + "\n",
                         encoding="utf-8")
