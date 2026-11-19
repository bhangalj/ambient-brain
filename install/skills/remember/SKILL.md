---
name: remember
description: Capture a durable memory into the portable brain vault. Use when the user says "remember this", "/remember", or wants to store a fact, person, project update, task, meeting, email, or file into their ambient brain. Detects input type (file path → parse, URL → fetch, raw text → distill), preserves raw sources immutably, distills into the right entity page, updates the index, commits + pushes.
---

# /remember: ingest into the ambient brain

The vault is the `__VAULT_DIR__` path in the "Ambient Brain" block of
`~/.claude/CLAUDE.md` (default `~/brain`). Read `<vault>/AGENTS.md` once per
session before you write. Do steps 1 to 6 in order.

## 1. Never store

- Write no secrets, credentials, API keys, tokens, `.env` contents or regulated
  PII to the vault. Git history is permanent.
- Before you write text to `sources/` or to any page, find every match of the
  canonical redaction list in `<vault>/AGENTS.md` → "Never store", and anything
  password- or token-shaped. Replace each match with `[REDACTED]`.
- If the content is fundamentally a secret, write nothing. Refuse and tell the user.

## 2. Entity pages

Every path writes to these pages. Apply these rules to each page you touch:

- Page by type: person → `people/<slug>.md` · project →
  `projects/<slug>/_project.md` · durable fact, concept, reference →
  `topics/<slug>.md` · meeting → `meetings/YYYY-MM-DD-<slug>.md`.
- Frontmatter on every page: `type`, `updated` (today, `YYYY-MM-DD`), plus the
  per-type keys in AGENTS.md → "Entity schemas". `people:` and `projects:` are
  arrays of wikilinks. `people:` lists who is RELEVANT, not who was present.
- Edit an existing page in place. Set its `updated:` to today.
- Slugs are kebab-case and never change. Check a person slug in
  `people/_index.md` (or the People section of `index.md` while `people/` is
  not sharded) before you link it. Invent no slugs.
- Alias-link every person and project on first use per page:
  `[[people/jane-doe|Jane]]`, `[[projects/acme/_project|Acme]]`.
- Store no snapshot counts (inventory tallies, installed versions). Keep a
  number only when it drives a decision or is the finding.
- A project with a `<name>.data.yml` companion gets new data in that file.
  Store nothing computable.

## 3. Route the input

Read the ONE reference file that matches the input. The first match in this
list wins. Do every step in it, then come back to step 4. The `references/`
folder sits beside this SKILL.md, not in the vault.

- Pasted transcript or long text → `references/transcript.md`
- File path (PDF, DOCX, PPTX, XLSX, image) or URL → `references/file-or-url.md`.
- Something the user must do, has finished, or waits on → `references/task-change.md`
- Short fact, or a person or project update → `references/fact.md`

A reference file sends you to `references/task-change.md` when its input also
holds a task. Follow that pointer every time.

## 4. Index

For each page you created, add one line. For each page you changed, make sure
its line still describes it.

1. Page under a content hub (for example `topics/<hub>/`) → that hub's `_index.md`.
2. Else, if `<section>/_index.md` exists (`people/`, `projects/`, `topics/`,
   `meetings/`) → that catalog. Keep the fuller hook there.
3. Else → the section in `index.md`. One terse line, ≤ ~80 characters.

The `index.md` pointer to a sharded section stays generic: no page counts, no
date ranges.

## 5. Commit and push

Run from the vault root.

1. Local-only vault: if `git -C <vault> remote` prints nothing, the vault has
   no remote by design. Do steps 3 to 5 only: skip the preflight, the pull and
   the push. Never add a remote or suggest one.
2. Preflight: `git -C <vault> ls-remote -q origin HEAD` must succeed. If it
   fails, run `bash <vault>/bootstrap.sh` (idempotent; it re-pins the
   repo-local credential helper to the remote's owner) and follow any WARN it
   prints (`gh auth login` as the owner). NEVER `gh auth switch`: it flips
   global state under parallel sessions.
3. Stage ONLY the paths this run wrote: `git -C <vault> add -- <path> [<path> …]`.
   Other sessions edit this vault in parallel. `git add -A`, `git add .` and
   `git commit -a` would commit their work under your message.
4. Run `git -C <vault> diff --cached --name-only`. It must list your paths and
   nothing else. Unstage any other path with
   `git -C <vault> restore --staged -- <path>` and leave the file as it is. On
   a dirty tree, carry on with your own paths.
5. `git -C <vault> commit -m "remember: <slug>"`
6. `git -C <vault> pull --rebase`. If it stops on a conflict, run
   `git -C <vault> rebase --abort`, keep the local commit, report the conflict,
   and stop.
7. `git -C <vault> push`. On rejection, retry once. If it stays blocked, keep
   the local commit, report the exact command to run, and stop.

## 6. Report

- The paths written and the index lines added.
- `tasks.md`: lines added, moved, merged and deleted, how the `## Now` cap was
  handled, and any overdue `## Blocked` line.
- Foreign changes in the tree that you left alone.
