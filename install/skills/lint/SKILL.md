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

Always full-vault regardless: `lint.py` (index cap, frontmatter, broken links,
orphans, undistilled sources, `tasks.md` rules) and the cheap-grep
never-store-leaks check (named in "## Checks" below).

`/lint full` (user says "full") → deep-check the entire vault, ignoring BASE.
Say which mode ran and what the diff base was.

Run `python3 -I <this skill's folder>/scripts/lint.py --vault <vault>` first
(`scripts/` sits beside this SKILL.md). It covers the checks with one right
answer, full vault, and prints one
`<CHECK>\t<path[:line]>\t<detail>` line per violation (nothing when clean).
Turn each line into a finding under the check it belongs to; do not re-check
what it covers. It also flags frontmatter (`FRONTMATTER`: base keys and the
per-type keys in AGENTS.md "Entity schemas") and broken wikilinks (`BROKEN_LINK`).

## Checks (group findings, most-important first)
1. **Contradictions** — pages asserting incompatible facts.
2. **Stale claims** — dated statements likely outdated; old frontmatter `updated`.
   Also flag snapshot counts and installed versions (AGENTS.md, "No snapshot
   counts") and propose removing them.
3. **Orphan pages** — `lint.py` reports them (`ORPHAN`). A link from `index.md`
   or a shard `_index.md` counts as an index entry.
4. **Missing cross-refs** — a page names a person/project that has a page but
   isn't wikilinked to it. Scan the **changed set only**: build the entity-name
   list from `people/`+`projects/` slugs and their `name:` frontmatter, then for
   each changed page grep those names appearing as bare text with no enclosing
   `[[…]]`. No single BSD-grep pass does the negative match — grep the bare name,
   then drop the hits already inside a `[[…]]`.
5. **Never-distilled sources** — `lint.py` reports them (`UNDISTILLED`). It
   honours every `sources/**/SKIPPED.md` list (list entries only, matched on
   filename stem) and folder citations, and skips infrastructure files.
   **If a source genuinely should not be distilled, the fix is to add it to
   `SKIPPED.md` with a reason and a date.**
6. **Index-cap violations** — `lint.py` reports lines over 80 characters
   (`INDEX_CAP`), duplicates (`INDEX_DUP`) and a hub pointer that holds a count
   or date range (`INDEX_POINTER`). Judge the rest yourself: a section grown past
   a screen (propose sharding via the `_index` hub pattern in AGENTS.md), and a
   count or date range in an `_index.md` header or in any `index.md` line that
   does not point at an `_index` hub. The strict cap binds `index.md` only;
   `_index.md` catalogs keep the fuller hook.
7. **`tasks.md` hygiene** — enforce the horizon convention (AGENTS.md →
   "Tasks: sections"). `lint.py` reports stray task lines before the first
   heading (`TASKS_STRAY`), wrong, missing, duplicate or out-of-order headings
   (`TASKS_HEADINGS`), an 8th `## Now` line (`TASKS_NOW_CAP`), a `## Blocked`
   line without `(waiting on` (`TASKS_BLOCKED`), `(waiting on` in Now, Next or
   Later (`TASKS_WAITING`), a capture date that is not a real date
   (`TASKS_DATE`), and a Next or Later line captured over 21 days ago
   with no deadline (`TASKS_EXPIRED`; a deadline is `⏰` or "by/before/due/until/
   target <date>"). For each, propose a fix: move the line, demote the lowest-pressure
   `## Now` line, or give an expired line a deadline, demote it to `## Later`
   (from `## Next`) or delete it.
   Judge the rest yourself:
   - **`## Now` pressure** — a `## Now` line with no real deadline within ~2
     weeks and no named person blocked on it belongs in `## Next`.
   - **Mis-domained items** — a personal-life item (home, personal
     finance, health, family, admin; anything sourced from a
     personal-life project or topic page) sitting outside `## Personal`. Domain
     beats shape: a personal *research* or *code* task still belongs in
     `## Personal`. Conversely flag a work item that has drifted into
     `## Personal`.
   - **Ordering** — `## Now` sorted soonest-deadline-first; `## Next`,
     `## Blocked`, and `## Later` sorted newest-capture-first by the trailing
     `(YYYY-MM-DD)`; `## Personal` unchanged, newest-first. A low-severity
     finding; batch these rather than listing each.
   Never delete a task yourself — this check proposes, the vault owner decides.
8. **Never-store leaks** — scan for the secret patterns in the canonical
   redaction list (AGENTS.md, "Never store"); flag loudly. Require a real
   secret-shaped **value** (a live token/key/password) — prose that merely
   mentions "Bearer" / "token" / "API key" while describing auth is a benign
   false positive; verify the match is an actual credential before flagging.
9. **GAP flags** — only when the user gives you `GAP:` lines (agents write them
   per the "Flag gaps" rule in `~/.claude/CLAUDE.md`). Check each against the
   page it names. A flag is a claim, not a fact: propose its fix only when the
   vault or the named source proves it.

## Rules
- **Propose first.** Present findings + proposed edits; apply ONLY on user OK.
- **Local-only vault:** if `git -C <vault> remote` prints nothing, skip the
  preflight, `pull --rebase` and `push` below; stage and commit only.
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
  owner. On a dirty tree, commit your own paths and say in the
  report which foreign changes you left alone.
  If `pull --rebase` stops on a conflict, run `git -C <vault> rebase --abort`, keep the
  local commit, and report the conflict. If the push stays blocked, keep the local commit
  and report the fix command.
- `/lint` guards the index cap, the `tasks.md` horizon convention (section
  order, the 7-item `## Now` cap, the `## Blocked` `(waiting on <name>)` tag,
  and the 21-day expiry rule), and the never-store rule. On tasks it always
  PROPOSES — it never deletes a task on its own; the vault owner decides.
