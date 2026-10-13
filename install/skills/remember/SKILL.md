---
name: remember
description: Capture a durable memory into the portable brain vault. Use when the user says "remember this", "/remember", or wants to store a fact, person, project update, meeting, email, or file into their ambient brain. Detects input type (file path → parse, URL → fetch, raw text → distill), preserves raw sources immutably, distills into the right entity page, updates the index, commits + pushes.
---

# /remember — ingest into the ambient brain

Vault path = the `__VAULT_DIR__` in the "Ambient Brain" block of the user's
global `~/.claude/CLAUDE.md` (default `~/brain`). Read `<vault>/AGENTS.md` first
if you have not this session.

## Steps
1. **Classify input:**
   - **Fathom meeting ingest** ("ingest new/latest Fathom meetings", or any
     Fathom recording) → follow `references/fathom-ingest.md` (own-recordings-only
     scope, delta-vs-`meetings/_index.md`, transcript→source→note→projects→tasks→
     indexes). It specialises the steps below for the recurring meeting pass.
   - Filesystem path (PDF/DOCX/PPTX/XLSX/image) → parse it to clean text with
     your document-extraction tool of choice; save the extract to
     `<vault>/sources/`.
   - URL → WebFetch; save fetched text to `<vault>/sources/`.
   - Pasted transcript / long block → save verbatim to `<vault>/sources/`.
   - Short one-line fact → skip `sources/`, go straight to the entity page.
2. **Redact before writing to `sources/`:** strip the secret patterns in the
   canonical redaction list in `<vault>/AGENTS.md` ("Never store"). If the
   content is fundamentally a secret, refuse (never-store rule, same section).
3. **Distill into entity page(s)** per AGENTS.md:
   - person → `<vault>/people/<slug>.md`
   - project → `<vault>/projects/<slug>/_project.md`
   - durable fact / concept / reference → `<vault>/topics/<slug>.md`
   - meeting → `<vault>/meetings/YYYY-MM-DD-<slug>.md`
   Apply frontmatter + wikilinks + stable kebab slugs; cross-link every
   person/project mentioned.
4. **Maintain `<vault>/tasks.md`** (the open-task working set):
   - **First, apply the bar** (AGENTS.md → "Tasks: what earns a line"). A task is
     **material work with a real outcome** — something to build, decide, or take
     to a named person. **Do NOT create tasks for** mechanical steps inside work
     already in flight (commit/push/merge/bump/update-the-doc), verifying your
     own recent change, passive "watch this" items, facts you could look up right
     now, or restatements of a project that already has a page. When it does not
     clear the bar, **write it on the project page instead** — that is the
     default, not the fallback. Be as willing to **delete** a finished line as to
     add a new one; a stale line in `tasks.md` costs more than a stale paragraph
     anywhere else, because this file is read as "what do I do this week".
   - New action item owned by the user → append a line, **under the right
     heading** (see AGENTS.md → "Tasks: sections" for the full horizon
     convention), newest-capture-first except in `## Now` which sorts
     soonest-deadline-first:
     `- **<task>** … — [[meetings/YYYY-MM-DD-<slug>|src]] (YYYY-MM-DD)` — the
     line format itself is UNCHANGED by the horizon convention, and the
     trailing date is the CAPTURE date, not a deadline.
     **Route by horizon, asking the questions in this order.** Life outside
     work (home, personal finance, health, family, personal admin) →
     `## Personal` at the bottom, flat and newest-first, *even when the task is
     research or a code change* and *even when it has a near-term deadline* —
     domain beats horizon. For everything else, ask in order: is there a real
     deadline within ~2 weeks, or is a named person blocked waiting on this →
     `## Now` (hard cap 7; if it already holds 7 lines, do not silently file an
     eighth — demote the least-urgent existing `## Now` line to `## Next`,
     delete it if it is no longer real, or route the new one to `## Next`
     instead, and say which you did in the report). Cannot progress because a
     named person or vendor owes something → `## Blocked`, and the line MUST
     carry `(waiting on <name>)`. A quarter or more away, or genuinely no
     urgency → `## Later`. Otherwise → `## Next`, newest-first — actionable
     with no date pressure, and the default for a new work task.
     Never leave a task line outside a heading — in particular, never let one
     land inside the header blockquote.
   - Input reports something finished/obsolete → **delete its line** (never
     mark or archive; git history is the record).
   Meeting notes keep the full action-item log for all owners; `tasks.md`
   holds only the user's currently-open items, with any dependency on a named
   person or vendor filed in `## Blocked` via `(waiting on <name>)`, not
   scattered inline through the other sections.
5. **Update the index / shard catalog:** add or edit the one-line entry for any
   page created or changed. **Route it to the section's `_index.md` catalog when
   the section is sharded** — a `topics/` page → `topics/_index.md`, a `people/`
   page → `people/_index.md`, a `meetings/` page → `meetings/_index.md` (the
   Fathom ref handles meetings). A leaf under a content hub (e.g. a new dataset
   page under `topics/<hub>/`) goes in that hub's `_index.md`, not the
   top-level `topics/_index.md`. Sections still listed inline in `index.md`
   get their line in `index.md`. Respect the index cap and the `_index` hub
   pattern (AGENTS.md, "The index cap"): the root `index.md` pointer for a
   sharded section stays **generic — no page counts or date ranges that rot**;
   the fuller hook lives in the catalog.
6. **Auth preflight, then commit + push** from the vault root:
   - **Local-only vault:** if `git -C <vault> remote` prints nothing, the vault
     has no remote by design. Skip the preflight, `pull --rebase` and `push`;
     just stage and commit as below. Never add a remote or suggest one.
   - Preflight: `git -C <vault> ls-remote -q origin HEAD` must succeed. If it
     fails, the repo-local credential helper is missing or the vault owner is
     not in gh's keyring: run `bash <vault>/bootstrap.sh` (idempotent; re-pins
     the helper to the remote's owner) and follow any WARN it prints
     (`gh auth login` as the owner). NEVER `gh auth switch` — it flips global
     state under parallel sessions.
   - Then stage **only the files this run wrote**. **Never `git add -A`, never
     `git add .`, never `git commit -a`.** Other sessions edit this vault in
     parallel, and a blanket stage commits their in-flight work under your
     `remember:` message — the change is then mislabelled in history and lands
     before its owner has reviewed it. Pass the exact paths from step 7:
     `git -C <vault> add -- <path> [<path> …] && git -C <vault> commit -m "remember: <slug>" && git -C <vault> pull --rebase && git -C <vault> push`
   - **Check the staged set before committing.** Run
     `git -C <vault> diff --cached --name-only` and confirm it lists your paths
     and nothing else. If a file you did not write is staged, unstage it with
     `git -C <vault> restore --staged -- <path>` and leave it in the working
     tree for whoever owns it. A dirty tree is never a reason to abort — commit
     your own paths and say in the report which foreign changes you left alone.
     Retry the push once on rejection. If the push stays blocked, keep the
     local commit, report exactly what to run, and stop — never lose the write.
7. Report the paths written and the index line(s) added.
