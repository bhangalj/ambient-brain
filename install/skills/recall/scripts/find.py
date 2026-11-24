#!/usr/bin/env python3
import argparse
import re
import sys
from pathlib import Path

DIRS = ("people", "projects", "topics", "meetings")
SUFFIXES = {".md", ".yml", ".txt"}
STOP = {"a", "an", "and", "about", "do", "does", "for", "how", "i", "in", "is", "know", "me", "my", "of", "on", "or",
        "the", "to", "what", "when", "where", "who", "why"}
WIDTH = 160
SHOW = 5


def clip(line: str, at: int, width: int) -> str:
    if len(line) <= width:
        return line
    start = max(0, min(at - width // 3, len(line) - width))
    return ("…" if start else "") + line[start:start + width] + ("…" if start + width < len(line) else "")


def sections(lines: list[str], markdown: bool):
    chain, start, fence = [], 1, False
    for i, line in enumerate(lines, 1):
        if line.startswith(("```", "~~~")):
            fence = not fence
        m = None if fence or not markdown else re.match(r"(#{1,6})\s+\S", line)
        if m:
            if i > start:
                yield start, i - 1, " > ".join(h for _, h in chain) or "(top)"
            chain = [(lvl, h) for lvl, h in chain if lvl < len(m.group(1))] + [(len(m.group(1)), line.strip())]
            start = i
    if lines:
        yield start, len(lines), " > ".join(h for _, h in chain) or "(top)"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("terms")
    ap.add_argument("--vault", required=True)
    ap.add_argument("--sources", action="store_true")
    ap.add_argument("--max-bytes", type=int, default=6000)
    a = ap.parse_args()
    vault = Path(a.vault)
    words = a.terms.lower().split()
    terms = list(dict.fromkeys(t for t in words if t not in STOP)) or list(dict.fromkeys(words))
    terms = list(dict.fromkeys(t[:-1] if len(t) > 3 and t.endswith("s") else t for t in terms))
    rx = {t: re.compile(r"(?<!\w)" + re.sub(r"\\?[-_]", "[-_]", re.escape(t)), re.I) for t in terms}
    files = [vault / "tasks.md"] + [p for d in DIRS + (("sources",) if a.sources else ())
                                    for p in sorted((vault / d).rglob("*"))
                                    if p.suffix in SUFFIXES and p.is_file() and not any(x.startswith(".") for x in p.relative_to(vault).parts)]
    found = []
    for f in files:
        if not f.is_file():
            continue
        rel = f.relative_to(vault).as_posix()
        in_path = {t for t, r in rx.items() if r.search(rel.split("/", 1)[-1])}
        lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
        if f.suffix == ".md" and lines[:1] == ["---"]:
            close = next((i for i in range(1, len(lines)) if lines[i] == "---"), 0)
            lines[:close + 1] = [""] * (close + 1)
        for start, end, chain in sections(lines, f.suffix == ".md"):
            hit_lines, matched, hits, best = [], set(), 0, 0
            for n in range(start, end + 1):
                spans = [(t, m.start()) for t, r in rx.items() for m in r.finditer(lines[n - 1])]
                if spans:
                    on_line = {t for t, _ in spans}
                    hit_lines.append((n, min(s for _, s in spans), len(on_line)))
                    best = max(best, len(on_line))
                    matched |= on_line
                    hits += len(spans)
            if hits:
                found.append((-best, -len(matched), -len(in_path), -hits, rel, start, end, chain, f.stat().st_size, hit_lines, lines))
    found.sort(key=lambda x: x[4], reverse=True)
    found.sort(key=lambda x: x[:4])
    out, size, shown = [], 0, 0
    for _, neg_terms, _, neg_hits, rel, start, end, chain, fsize, hit_lines, lines in found:
        block = [f"{rel}:{start}-{end} ({fsize / 1024:.1f} KB) {chain} [{-neg_terms}/{len(terms)} terms, {-neg_hits} hits]"]
        top = sorted(sorted(hit_lines, key=lambda h: -h[2])[:SHOW])
        block += [f"  {n}: {clip(lines[n - 1], at, WIDTH)}" for n, at, _ in top]
        last = top[-1][0]
        if last < end and lines[last].strip() and len(hit_lines) <= SHOW:
            block.append(f"  {last + 1}- {clip(lines[last], 0, WIDTH // 2)}")
        if len(hit_lines) > SHOW:
            block.append(f"  … {len(hit_lines) - SHOW} more matching lines in this section")
        text = "\n".join(block) + "\n"
        if shown and size + len(text.encode()) > a.max_bytes:
            break
        out.append(text)
        size += len(text.encode())
        shown += 1
    hidden = found[shown:]
    if hidden:
        tail = (f"[find] {shown} of {len(found)} sections shown; {sum(-h[3] for h in hidden)} hits in {len(hidden)} sections not shown"
                " — narrow with a rarer term, a slug, or fewer common words")
    else:
        tail = f"[find] {len(found)} sections, {sum(-h[3] for h in found)} hits, all shown (terms: {' '.join(terms)})"
    sys.stdout.write("".join(out) + tail + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
