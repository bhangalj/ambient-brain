---
name: recall
description: Look something up in the portable brain vault. Read-only. Use when the user says "/recall", "what do I know about X", "check my brain/notes for", or when a task depends on stored context (a person, project, decision, or preference). Reads index → entity page → depth, answers with file-path citations. Never writes or commits.
---

# /recall — read the ambient brain (READ ONLY)

Vault path = `__VAULT_DIR__` from the "Ambient Brain" block of global
`~/.claude/CLAUDE.md` (default `~/brain`).

## Steps
0. **Tasks shortcut:** if the ask is "outstanding tasks", "what's on my
   plate", "open action items" or similar → read `<vault>/tasks.md` and answer
   from it (every line there is open by definition). Meeting-note action items
   are the historical log, NOT the tracker — don't grep them for open tasks.
1. Read `<vault>/index.md` to find candidate entity pages.
2. Open the matching page(s) under `people/ projects/ topics/ meetings/`.
3. Only if the page points deeper, follow wikilinks or read `<vault>/sources/`.
4. Answer concisely, **citing the file path(s)** used (e.g.
   `topics/acme-fiscal-calendar.md`).
5. **Never write, never commit.** If the brain is missing something the user
   clearly wants stored, suggest `/remember` — do not write it yourself.
   Read-only also means no git auth is ever needed here; remote pushes (and
   their auth preflight) live in `/remember` and `/lint` only.
