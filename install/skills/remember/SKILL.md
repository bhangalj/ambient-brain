---
name: remember
description: Capture a durable memory into the portable brain vault. Use when the user says "remember this", "/remember", or wants to store a fact, person, project update, meeting, email, or file into their ambient brain. Detects input type (file path → liteparse, URL → fetch, raw text → distill), preserves raw sources immutably, distills into the right entity page, updates the index, commits + pushes.
---

# /remember — ingest into the ambient brain

Vault path = the `__VAULT_DIR__` in the "Ambient Brain" block of the user's
global `~/.claude/CLAUDE.md` (default `~/brain`). Read `<vault>/AGENTS.md` first
if you have not this session.

## Steps
1. **Classify input:**
   - Filesystem path (PDF/DOCX/PPTX/XLSX/image) → `lit parse <path>` for clean
     text; save the extract to `<vault>/sources/`.
   - URL → WebFetch; save fetched text to `<vault>/sources/`.
   - Pasted transcript / long block → save verbatim to `<vault>/sources/`.
   - Short one-line fact → skip `sources/`, go straight to the entity page.
2. **Redact before writing to `sources/`:** strip `sk-[A-Za-z0-9]{20,}`,
   `gho_[A-Za-z0-9]+`, `AKIA[0-9A-Z]{16}`, `Bearer [A-Za-z0-9._-]+`, and
   anything password/token-shaped. If the content is fundamentally a secret,
   refuse (never-store rule in AGENTS.md).
3. **Distill into entity page(s)** per AGENTS.md:
   - person → `<vault>/people/<slug>.md`
   - project → `<vault>/projects/<slug>/_project.md`
   - durable fact / concept / reference → `<vault>/topics/<slug>.md`
   - meeting → `<vault>/meetings/YYYY-MM-DD-<slug>.md`
   Apply frontmatter + wikilinks + stable kebab slugs; cross-link every
   person/project mentioned.
4. **Update `<vault>/index.md`:** add/edit the one-line entry for any page
   created or changed, respecting the cap (≤ ~80 chars).
5. **Commit + push** from the vault root:
   `git -C <vault> add -A && git -C <vault> commit -m "remember: <slug>" && git -C <vault> pull --rebase && git -C <vault> push`
   Retry the push once on rejection.
6. Report the paths written and the index line(s) added.
