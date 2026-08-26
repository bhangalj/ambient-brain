---
name: lint
description: Reconcile and health-check the portable brain vault. Use when the user says "/lint", "clean up my brain", "check my notes for contradictions", or periodically. Sweeps for contradictions, stale claims, orphan pages, missing cross-references, never-distilled sources, and index-cap violations. Proposes fixes and commits only on the user's OK.
---

# /lint — reconcile the ambient brain (propose, then commit on OK)

Vault path = `__VAULT_DIR__` from the "Ambient Brain" block of global
`~/.claude/CLAUDE.md` (default `~/brain`). Read `<vault>/AGENTS.md` first if you
have not this session — it holds the canonical redaction list and the index cap
that the never-store-leaks and index-cap checks enforce.

## Scope — incremental by default
Deep checks (contradictions, stale claims, cross-refs) run only on pages
**changed since the last lint commit**:
```
BASE=$(git -C <vault> log --grep='^lint:' -1 --format=%H)   # empty → full sweep
git -C <vault> diff --name-only $BASE -- '*.md'             # the deep-check set
```
Plus: when a changed page contradicts an unchanged one, pull the unchanged page
into the set too (follow its wikilinks one hop).

Always full-vault regardless (cheap greps, no file reads): the index-cap,
`tasks.md`-hygiene, stale-ingest-branch, never-store-leaks, orphan-pages,
and never-distilled-sources checks (named in "## Checks" below).

`/lint full` (user says "full") → deep-check the entire vault, ignoring BASE.
Say which mode ran and what the diff base was.

## Checks (group findings, most-important first)
1. **Contradictions** — pages asserting incompatible facts.
2. **Stale claims** — dated statements likely outdated; old frontmatter `updated`.
3. **Orphan pages** — entity pages with no inbound wikilink and no index entry.
   A line in a section's `_index.md` shard catalog counts as an index entry —
   `people/`, `topics/`, and `meetings/` pages are catalogued there, not in
   `index.md`, so grep the shards too before calling a page orphaned.
4. **Missing cross-refs** — a page names a person/project that has a page but
   isn't wikilinked to it. Scan the **changed set only**: build the entity-name
   list from `people/`+`projects/` slugs and their `name:` frontmatter, then for
   each changed page grep those names appearing as bare text with no enclosing
   `[[…]]`. No single BSD-grep pass does the negative match — grep the bare name,
   then drop the hits already inside a `[[…]]`.
5. **Never-distilled sources** — files in `sources/` no entity page derives from.
   **Exclusion sets are MANDATORY; without them this check cries wolf every run.**
   - **Read every deliberate-skip list.** `sources/SKIPPED.md` covers any file
     under `sources/`, and a subfolder may carry its own (for example
     `sources/<feed>/SKIPPED.md`, which a background ingest for that feed reads
     too — so entries for that feed belong there). Anything listed in one of
     these was consciously not distilled and **must not be reported**. That file
     documents its own matcher: compare **filename stems**, accepting
     `<date>/<name>.md`, `<name>.md` and a bare `<name>`. A background ingest
     already honours it; the lint must too, or the same file is re-flagged
     forever — which is exactly what happens to a low-value transcript someone
     skipped on purpose months ago.
   - **Infrastructure files are not sources.** Skip `INDEX.md`, `SKIPPED.md`,
     ingest scripts, `.gitkeep`, `.DS_Store`, and anything else that is tooling
     or a catalog rather than ingested material.
   Runnable form:
   ```python
   import os, re, glob
   pages = "\n".join(open(p, encoding="utf-8").read() for p in
                     glob.glob("**/*.md", recursive=True)
                     if not p.startswith(("sources/", "install/", ".git")))
   skipped = set()
   for sk in glob.glob("sources/**/SKIPPED.md", recursive=True) + ["sources/SKIPPED.md"]:
       if not os.path.exists(sk):
           continue
       for line in open(sk):                      # LIST ENTRIES ONLY -- parsing every
           if not line.lstrip().startswith("- "): # backtick also catches the file's own
               continue                           # prose ("run.sh", "<name>") and would
           m = re.search(r"`([^`]+)`", line)      # silently hide real sources
           if m:
               skipped.add(os.path.splitext(os.path.basename(m.group(1)))[0])
   INFRA = {"INDEX", "SKIPPED", ".gitkeep", ".DS_Store"}
   for s in glob.glob("sources/**/*", recursive=True):
       if not os.path.isfile(s):
           continue
       stem = os.path.splitext(os.path.basename(s))[0]
       if stem in skipped or stem in INFRA or stem.startswith("."):
           continue
       if s.endswith((".py", ".sh")):             # ingest tooling, not material
           continue
       if stem not in pages and s not in pages:
           print("UNDISTILLED:", s)
   ```
   **If a source genuinely should not be distilled, the fix is to add it to
   `SKIPPED.md` with a reason and a date — never to silently ignore it.**
6. **Index-cap violations** — `index.md` lines over the index cap (AGENTS.md,
   "The index cap"), duplicates, or a section grown past a screen (propose
   sharding via the `_index` hub pattern documented there). Three refinements:
   - **Measure characters, not bytes.** Multibyte glyphs (`→ ↔ · €`) inflate a
     naive BSD `awk length()`; use a UTF-8-aware count — `python3` (`len()` on
     the rstripped line) is the reliable one on stock macOS (`wc -m` is
     locale-dependent, `gawk` isn't installed) — so lines that are ≤80
     *characters* aren't false-flagged.
   - **`_index.md` catalogs sit one hop deeper**, so the strict ≤80 relaxes there
     — still one line per page, but keep the fuller hook. The strict cap binds
     `index.md` only.
   - **Rotting pointer facts.** Flag a hardcoded page count or date range in an
     `index.md` (or `_index.md` header) pointer/summary line — it goes stale as
     pages change; pointers stay generic.
7. **`tasks.md` hygiene** — enforce the horizon convention (AGENTS.md →
   "Tasks: sections"). Cheap, so run it every lint regardless of the diff base.
   Flag:
   - **Stray task lines** outside a heading — any `- ` line before the first
     `## ` heading, including one wedged inside the header blockquote (this has
     happened; it silently hides the task from the human eye). Move it to the
     section it belongs in.
   - **Section order / unknown headings** — exactly `## Now`, `## Next`,
     `## Blocked`, `## Later`, `## Personal`, in that order, each at most once;
     `## Personal` last.
   - **`## Now` cap** — hard cap of 7 lines. Flag an 8th; propose demoting the
     lowest-pressure line to `## Next` or deleting it. Also flag a `## Now`
     line with no real deadline within ~2 weeks and no named person blocked on
     it — it belongs in `## Next` instead.
   - **`## Blocked` format** — every line must carry `(waiting on <name>)`.
     Flag a `## Blocked` line missing it, and flag the inline `(waiting on …)`
     pattern surfacing in `## Now`, `## Next`, or `## Later` — that line should
     move to `## Blocked` instead.
   - **Mis-domained items** — a personal-life item (property, mortgage /
     personal finance, health, family, personal admin; anything sourced from a
     personal-life project or topic page) sitting outside `## Personal`. Domain
     beats shape: a personal *research* or *code* task still belongs in
     `## Personal`. Conversely flag a work item that has drifted into
     `## Personal`.
   - **Expiry** — a `## Next` or `## Later` line whose trailing capture date is
     more than 21 days old and carries no deadline. Propose one of: give it a
     deadline, demote it to `## Later` (from `## Next`), or delete it. Never
     delete it yourself — this check proposes, the vault owner decides.
   - **Ordering** — `## Now` sorted soonest-deadline-first; `## Next`,
     `## Blocked`, and `## Later` sorted newest-capture-first by the trailing
     `(YYYY-MM-DD)`; `## Personal` unchanged, newest-first. A low-severity
     finding; batch these rather than listing each.
8. **Stale ingest branch** — if the vault runs a background ingest (something
   under `install/` that distils new material onto a rolling branch behind a
   draft PR), the SessionStart hook is usually the only thing that surfaces it.
   Back that up here, since a `/lint` is exactly when an unnoticed backlog
   should surface. With `<branch>` as that ingest branch:
   ```
   git -C <vault> rev-list --count main..<branch> 2>/dev/null    # 0 or no branch → nothing pending
   git -C <vault> log -1 --format=%cr main..<branch> 2>/dev/null # how long it has sat
   ```
   Flag a branch **older than ~3 days** as a finding: unmerged notes are
   invisible to `/recall`, so the vault is quietly missing context it already
   has. The fix is a human merge — propose it, never merge it yourself, and give
   the branch explicitly, since by then you are on `main` and a bare
   `gh pr merge` would look for a PR for `main`:
   `gh pr merge <branch> --squash --delete-branch` (from the vault, with the
   owner's token — AGENTS.md, "Git auth on multi-account machines").
   Also read the ingest's status file if it writes one (typically
   `<vault>/.git/<ingest>.status`, tab-separated `state`/`when`/`why`): a
   leading `error` means the job itself is broken, and a leading `skipped` whose
   timestamp is days old means it has been deferring every run without ever
   working — both need reporting even when no branch exists.
9. **Never-store leaks** — scan for the secret patterns in the canonical
   redaction list (AGENTS.md, "Never store"); flag loudly. Require a real
   secret-shaped **value** (a live token/key/password) — prose that merely
   mentions "Bearer" / "token" / "API key" while describing auth is a benign
   false positive; verify the match is an actual credential before flagging.

## Rules
- **Propose first.** Present findings + proposed edits; apply ONLY on user OK.
- On confirmation: edit, then auth-preflight `git -C <vault> ls-remote -q origin HEAD`
  (on failure run `bash <vault>/bootstrap.sh` to re-pin the repo-local credential
  helper; never `gh auth switch`), then
  stage **only the files this run edited** — **never `git add -A`, never `git add .`,
  never `git commit -a`.** Other sessions edit this vault in parallel, and a blanket
  stage commits their in-flight work under your `lint:` message, mislabelling it in
  history and landing it before its owner has reviewed it. Pass the exact paths:
  `git -C <vault> add -- <path> [<path> …] && git -C <vault> commit -m "lint: <summary>" && git -C <vault> pull --rebase && git -C <vault> push`.
  Before committing, run `git -C <vault> diff --cached --name-only` and confirm it lists
  your paths and nothing else; unstage any stranger with
  `git -C <vault> restore --staged -- <path>` and leave it in the working tree for its
  owner. A dirty tree is never a reason to abort — commit your own paths and say in the
  report which foreign changes you left alone.
  If the push stays blocked, keep the local commit and report the fix command.
- `/lint` guards the index cap, the `tasks.md` horizon convention (section
  order, the 7-item `## Now` cap, the `## Blocked` `(waiting on <name>)` tag,
  and the 21-day expiry rule), and the never-store rule. On tasks it always
  PROPOSES — it never deletes a task on its own; the vault owner decides.
