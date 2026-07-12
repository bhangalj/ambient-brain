---
name: lint
description: Reconcile and health-check the portable brain vault. Use when the user says "/lint", "clean up my brain", "check my notes for contradictions", or periodically. Sweeps for contradictions, stale claims, orphan pages, missing cross-references, never-distilled sources, and index-cap violations. Proposes fixes and commits only on the user's OK.
---

# /lint — reconcile the ambient brain (propose, then commit on OK)

Vault path = `__VAULT_DIR__` from the "Ambient Brain" block of global
`~/.claude/CLAUDE.md` (default `~/brain`).

## Scope — incremental by default
Deep checks (contradictions, stale claims, cross-refs) run only on pages
**changed since the last lint commit**:
```
BASE=$(git -C <vault> log --grep='^lint:' -1 --format=%H)   # empty → full sweep
git -C <vault> diff --name-only $BASE -- '*.md'             # the deep-check set
```
Plus: when a changed page contradicts an unchanged one, pull the unchanged page
into the set too (follow its wikilinks one hop).

Always full-vault regardless (cheap greps, no file reads):
index-cap (6), never-store leaks (7), orphan pages (3), never-distilled
sources (5).

`/lint full` (user says "full") → deep-check the entire vault, ignoring BASE.
Say which mode ran and what the diff base was.

## Checks (group findings, most-important first)
1. **Contradictions** — pages asserting incompatible facts.
2. **Stale claims** — dated statements likely outdated; old frontmatter `updated`.
3. **Orphan pages** — entity pages with no inbound wikilink and no index entry.
4. **Missing cross-refs** — a page names a person/project that has a page but
   isn't wikilinked to it.
5. **Never-distilled sources** — files in `sources/` no entity page derives from.
6. **Index-cap violations** — `index.md` lines over ~80 chars, duplicates, or a
   section grown past a screen (propose sharding/archiving).
7. **Never-store leaks** — scan for secret patterns (`sk-…`, `gho_…`, `AKIA…`,
   bearer tokens); flag loudly.

## Rules
- **Propose first.** Present findings + proposed edits; apply ONLY on user OK.
- On confirmation: edit, then
  `git -C <vault> add -A && git -C <vault> commit -m "lint: <summary>" && git -C <vault> pull --rebase && git -C <vault> push`.
- `/lint` guards the index cap and the never-store rule.
