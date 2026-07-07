---
name: recall
description: Look something up in the portable brain vault. Read-only. Use when the user says "/recall", "what do I know about X", "check my brain/notes for", or when a task depends on stored context (a person, project, decision, or preference). Reads index → entity page → depth, answers with file-path citations. Never writes or commits.
---

# /recall — read the ambient brain (READ ONLY)

Vault path = `__VAULT_DIR__` from the "Ambient Brain" block of global
`~/.claude/CLAUDE.md` (default `~/brain`).

## Steps
1. Read `<vault>/index.md` to find candidate entity pages.
2. Open the matching page(s) under `people/ projects/ topics/ meetings/`.
3. Only if the page points deeper, follow wikilinks or read `<vault>/sources/`.
4. Answer concisely, **citing the file path(s)** used (e.g.
   `topics/deepset-fiscal-calendar.md`).
5. **Never write, never commit.** If the brain is missing something the user
   clearly wants stored, suggest `/remember` — do not write it yourself.
