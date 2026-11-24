#!/usr/bin/env python3
import argparse
import glob
import os
import re
import sys
from datetime import date
from pathlib import Path

ENTITY_DIRS = ("people/", "projects/", "topics/", "meetings/")
SCHEMA = {"person": ("name",), "project": ("name", "status"), "project-doc": ("project",), "meeting": ("date",), "topic": (), "meta": ()}
STATUSES = ("active", "paused", "done", "idea")
SECTIONS = ["Now", "Next", "Blocked", "Later", "Personal"]
WIKILINK = re.compile(r"\[\[([^\]\n]+?)\]\]")
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)
CAPTURE = re.compile(r"\((\d{4}-\d{2}-\d{2})\)\s*$")
MONTH = r"(?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sept|sep|oct|nov|dec)\b"
DEADLINE = re.compile(r"⏰|\b(?:by|before|due|until|target)\s+(?:end of\s+|~)?(?:[a-z]{3}\s+)?"
                      r"(?:\d{4}-\d{2}-\d{2}|~?\d{1,2}\s+" + MONTH + r"|" + MONTH + r")", re.I)


def check_index() -> list[str]:
    out, seen = [], set()
    if not os.path.exists("index.md"):
        return out
    for n, line in enumerate(open("index.md", encoding="utf-8").read().split("\n"), 1):
        line = line.rstrip()
        if not line.startswith("- "):
            continue
        if len(line) > 80:
            out.append(f"INDEX_CAP\tindex.md:{n}\t{len(line)} characters, cap 80")
        if line in seen:
            out.append(f"INDEX_DUP\tindex.md:{n}\tduplicate of an earlier line")
        seen.add(line)
        if re.search(r"\[\[[^\]]*_index[\]|]", line) and re.search(r"\d", WIKILINK.sub("", line)):
            out.append(f"INDEX_POINTER\tindex.md:{n}\thub pointer holds a count or date range")
    return out


def check_frontmatter(entities: list[str]) -> list[str]:
    out = []
    for p in entities:
        m = FRONTMATTER.match(open(p, encoding="utf-8").read())
        if not m:
            out.append(f"FRONTMATTER\t{p}\tno frontmatter")
            continue
        fm = {k: v.strip().strip("'\"") for k, v in re.findall(r"^([\w-]+):[ \t]*(.*)$", m.group(1), re.M)}
        missing = [k for k in ("type", "updated", *SCHEMA.get(fm.get("type"), ())) if k not in fm]
        if missing:
            out.append(f"FRONTMATTER\t{p}\tmissing {', '.join(missing)}")
        if "type" in fm and fm["type"] not in SCHEMA:
            out.append(f"FRONTMATTER\t{p}\tunknown type: {fm['type']}")
        if "updated" in fm and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", fm["updated"]):
            out.append(f"FRONTMATTER\t{p}\tupdated is not YYYY-MM-DD: {fm['updated']}")
        if fm.get("type") == "project" and "status" in fm and fm["status"] not in STATUSES:
            out.append(f"FRONTMATTER\t{p}\tstatus not in {'|'.join(STATUSES)}: {fm['status']}")
    return out


def check_links_and_orphans(pages: list[str], entities: list[str]) -> list[str]:
    out, inbound = [], set()
    for p in pages:
        text = open(p, encoding="utf-8").read()
        for code in (r"(?ms)^(```|~~~).*?^\1", r"(?s)<!--.*?-->", r"(`+)[^`\n]*?\1"):
            text = re.sub(code, lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)
        for m in WIKILINK.finditer(text):
            target = re.split(r"[|#]", m.group(1))[0].strip().rstrip("\\")
            if target.startswith(("../", "./")):
                target = os.path.join(os.path.dirname(p), target)
            target = os.path.normpath(target)
            if not (os.path.exists(target) or os.path.exists(target + ".md")):
                out.append(f"BROKEN_LINK\t{p}:{text.count(chr(10), 0, m.start()) + 1}\t[[{m.group(1)}]]")
            if target.removesuffix(".md") != p.removesuffix(".md"):
                inbound.add(target.removesuffix(".md"))
    out += [f"ORPHAN\t{p}\tno inbound wikilink and no index entry" for p in entities if p.removesuffix(".md") not in inbound]
    return out


def check_undistilled() -> list[str]:
    out = []
    pages = "\n".join(open(p, encoding="utf-8").read() for p in
                      glob.glob("**/*.md", recursive=True)
                      if not p.startswith(("sources/", "install/", ".git")))
    skipped = set()
    for sk in glob.glob("sources/**/SKIPPED.md", recursive=True):
        for line in open(sk, encoding="utf-8"):
            if not line.lstrip().startswith("- "):
                continue
            m = re.search(r"`([^`]+)`", line)
            if m:
                skipped.add(os.path.splitext(os.path.basename(m.group(1)))[0])
    INFRA = {"INDEX", "SKIPPED", ".gitkeep", ".DS_Store"}
    for s in sorted(glob.glob("sources/**/*", recursive=True)):
        if not os.path.isfile(s) or "__pycache__" in s:
            continue
        stem = os.path.splitext(os.path.basename(s))[0]
        if stem in skipped or stem in INFRA or stem.startswith("."):
            continue
        d = os.path.dirname(s)
        folder_cited = d != "sources" and re.search(re.escape(d) + r"/?[\]\)`\s|]", pages)
        if stem not in pages and s not in pages and not folder_cited:
            out.append(f"UNDISTILLED\t{s}\tno page cites it and no SKIPPED.md lists it")
    return out


def check_tasks(today: date) -> list[str]:
    if not os.path.exists("tasks.md"):
        return []
    out, headings, items, section = [], [], [], None
    text = open("tasks.md", encoding="utf-8").read()
    fm = FRONTMATTER.match(text)
    offset = fm.group(0).count("\n") if fm else 0
    for n, line in enumerate(text[fm.end() if fm else 0:].split("\n"), offset + 1):
        if line.startswith("## "):
            section = line[3:].strip()
            headings.append((n, section))
        elif section is None:
            if re.sub(r"^[>\s]*", "", line).startswith("- ") or CAPTURE.search(line):
                out.append(f"TASKS_STRAY\ttasks.md:{n}\ttask line before the first ## heading")
        elif line.startswith("- "):
            items.append([n, section, line])
        elif line.strip() and line[0].isspace() and not line.lstrip().startswith("- ") and items and items[-1][1] == section:
            items[-1][2] += " " + line.strip()
    seen, last = set(), -1
    for n, name in headings:
        if name not in SECTIONS:
            out.append(f"TASKS_HEADINGS\ttasks.md:{n}\tunknown heading: ## {name}")
        elif name in seen:
            out.append(f"TASKS_HEADINGS\ttasks.md:{n}\tduplicate heading: ## {name}")
        elif SECTIONS.index(name) < last:
            out.append(f"TASKS_HEADINGS\ttasks.md:{n}\t## {name} out of order")
        if name in SECTIONS and name not in seen:
            last = max(last, SECTIONS.index(name))
        seen.add(name)
    out += [f"TASKS_HEADINGS\ttasks.md\tmissing heading: ## {s}" for s in SECTIONS if s not in seen]
    now = [i for i in items if i[1] == "Now"]
    if len(now) > 7:
        out.append(f"TASKS_NOW_CAP\ttasks.md:{now[7][0]}\t{len(now)} items in ## Now, cap 7")
    for n, sec, item in items:
        if sec == "Blocked" and "(waiting on" not in item:
            out.append(f"TASKS_BLOCKED\ttasks.md:{n}\t## Blocked line without (waiting on <name>)")
        if sec in ("Now", "Next", "Later") and "(waiting on" in item:
            out.append(f"TASKS_WAITING\ttasks.md:{n}\t(waiting on …) in ## {sec}; move it to ## Blocked")
        m = CAPTURE.search(item)
        if sec in ("Next", "Later") and m and not DEADLINE.search(item):
            try:
                age = (today - date.fromisoformat(m.group(1))).days
            except ValueError:
                out.append(f"TASKS_DATE\ttasks.md:{n}\tcapture date is not a real date: {m.group(1)}")
                continue
            if age > 21:
                out.append(f"TASKS_EXPIRED\ttasks.md:{n}\t## {sec} line captured {m.group(1)}, {age} days ago, no deadline")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault", default=str(Path.home() / "brain"))
    os.chdir(ap.parse_args().vault)
    pages = sorted(p for p in glob.glob("**/*.md", recursive=True) if not p.startswith(("sources/", "install/")))
    entities = [p for p in pages if p.startswith(ENTITY_DIRS)]
    found = (check_index() + check_frontmatter(entities) + check_links_and_orphans(pages, entities)
             + check_undistilled() + check_tasks(date.today()))
    if found:
        print("\n".join(found))
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
