---
name: lint
description: Reconcile and health-check the portable brain vault. Use when the user says "/lint", "clean up my brain", "check my notes for contradictions", or periodically. Sweeps for contradictions, stale claims, orphan pages, missing cross-references, never-distilled sources, and index-cap violations. Proposes fixes and commits only on the user's OK.
---

# /lint — reconcile the ambient brain (propose, then commit on OK)

Vault path = `__VAULT_DIR__` from the "Ambient Brain" block of global
`~/.claude/CLAUDE.md` (default `~/brain`).

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
