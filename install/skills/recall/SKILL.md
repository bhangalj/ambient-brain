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
   The file has five sections (AGENTS.md → "Tasks: sections"), split by
   horizon: `## Now` (hard-capped at 7, real deadline or someone blocked on
   it), `## Next` (actionable, no date pressure), `## Blocked` (waiting on a
   named person or vendor), and `## Later` (a quarter or more away, or no
   urgency) are work; `## Personal` is life outside work. **Answer in those
   groupings, and honour the scope in the ask** — a work-framed question
   ("what's on my plate at work", "before this review") means the four work
   sections; a personal question means `## Personal`. Only an unqualified
   "what's open" spans all five. If the ask is just "what's next" or a normal
   daily pass, `## Now` alone is the default read — the other sections are
   there but not implied.
1. Read `<vault>/index.md` to find candidate entity pages. When a section is
   **sharded** — `/lint` shards any section that outgrows a screen, and its
   `index.md` entry becomes a `[[<section>/_index]]` pointer — open that
   `_index.md` catalog to locate the specific page.
2. Open the matching page(s) under `people/ projects/ topics/ meetings/`.
3. Only if the page points deeper, follow wikilinks or read `<vault>/sources/`.
4. Answer concisely, **citing the file path(s)** used (e.g.
   `topics/acme-fiscal-calendar.md`).
5. **Never write, never commit.** If the brain is missing something the user
   clearly wants stored, suggest `/remember` — do not write it yourself.
   Read-only also means no git auth is ever needed here; remote pushes (and
   their auth preflight) live in `/remember` and `/lint` only.
