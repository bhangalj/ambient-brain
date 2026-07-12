---
type: meta
updated: 2026-01-01
---
# AGENTS.md — how to read and write this brain

This is a portable, git-backed **markdown memory vault** — an "ambient brain."
It holds durable, cross-session context: people, projects, durable knowledge,
and the meetings/emails/files worth keeping. **This repo is the single source
of truth** — nothing durable lives outside it. It is pure markdown: no runtime,
no database, no API key. Any agent or harness that can read files can use it.

## The three verbs

- **remember** — ingest something: preserve the raw in `sources/` (if it's a
  real source), distill it into the right entity page, update `index.md`,
  commit + push. (`/remember` skill.)
- **recall** — look something up: read `index.md` → the entity page → depth.
  Read-only, always cited. (`/recall` skill.)
- **lint** — reconcile: contradictions, stale claims, orphans, missing
  cross-refs, undistilled sources, index-cap. Proposes, commits on OK.
  (`/lint` skill.)

## Answering "what do I know about X?"

Read in this order; stop as soon as you have enough:

1. **`index.md`** — the map of the whole brain (loaded into every session).
2. **The entity page** — `people/<slug>.md`, `projects/<slug>/_project.md`,
   `topics/<slug>.md`, or `meetings/YYYY-MM-DD-<slug>.md`.
3. **Depth** — follow wikilinks between entity pages.
4. **Raw** — `sources/` holds the immutable original (transcript, email, parsed
   file) a page was distilled from. Re-read it to re-distill or verify.

## Layout

| Path | Holds |
|---|---|
| `AGENTS.md` | this file — THE agent entry point |
| `index.md` | one-line-per-page map of the brain; loaded every session; capped |
| `tasks.md` | open action items — the ONLY mutable task state; done = delete the line |
| `people/<slug>.md` | one page per person |
| `projects/<slug>/_project.md` | one page per project (state + docs hub) |
| `topics/<slug>.md` | durable concepts, facts, reference, ideas |
| `meetings/YYYY-MM-DD-<slug>.md` | cleaned, wiki-linked meeting notes |
| `sources/` | raw, **immutable** dropped-in material you ingest FROM |
| `install/` | the skills + global-CLAUDE.md snippet + `bootstrap.sh` (setup glue) |

## Conventions

- **Frontmatter on every note.** Base keys: `type`, `updated` (`YYYY-MM-DD`),
  plus per-type keys below. Use `people:` / `projects:` arrays of wikilinks.
- **Wikilinks for every person/project mention:** `[[people/jane-doe]]`,
  `[[projects/acme/_project|Acme]]`. This is the link graph — don't skip it.
- **Kebab-case slugs that NEVER change.** Slugs are identity; renaming breaks
  every wikilink and every agent's memory of the vault.
- **Dates are `YYYY-MM-DD`. Encoding is UTF-8.**
- **Tasks: log vs state.** Meeting notes are the immutable *log* of action
  items (all owners, never retro-edited to track completion); `tasks.md` is the
  mutable *state* — the user's currently-open items only. `/remember` appends
  new user-owned items and **deletes** finished ones (git history is the
  archive); `/recall` answers "outstanding tasks" from `tasks.md` alone.
  Starting empty is fine — declare task bankruptcy explicitly; anything still
  relevant will resurface.

Entity schemas:

```yaml
# people/<slug>.md
---
type: person
name: Jane Doe
updated: 2026-01-01
---
```
```yaml
# projects/<slug>/_project.md
---
type: project
name: My Project
status: active        # active | paused | done | idea
updated: 2026-01-01
people: ["[[people/jane-doe]]"]
---
# Body: ## State · ## How it works · ## Decisions · ## Log
```
```yaml
# topics/<slug>.md
---
type: topic
updated: 2026-01-01
---
```
```yaml
# meetings/YYYY-MM-DD-<slug>.md
---
type: meeting
date: 2026-01-01
people: ["[[people/jane-doe]]"]
project: "[[projects/acme/_project|Acme]]"
source: "[[../sources/<raw-file>]]"   # if a transcript/recording was ingested
updated: 2026-01-01
---
```

## The index cap

`index.md` is loaded into EVERY session, so it must stay lean: **one terse line
per entity page, ≤ ~80 characters** (name + hook). Depth always lives one file
deeper. `/lint` enforces this — trimming over-long lines, de-duping, and
sharding/archiving any section that outgrows a screen.

## Never store (hard rule)

This vault is a private git repo that pushes off-device; git history is
permanent. **Never store:** secrets, credentials, API keys, tokens, `.env`
contents, or regulated/customer PII you did not deliberately choose to keep.

On ingest, `/remember` redacts obvious secret patterns before writing to
`sources/`: `sk-…`, `gho_…`, `AKIA…`, `Bearer …`, and anything password-shaped.
If a source is fundamentally a secret, refuse and tell the user. `/lint` audits
for leaks.

## Precedence vs native memory

Durable, cross-session, or personal facts live HERE. Claude Code's native
per-project memory (`~/.claude/projects/*/memory/`) is only for disposable,
project-local progress notes — never put portable facts there.

## Bootstrap — stand this up on a new machine

The repo carries everything it needs. On a fresh machine:

```bash
git clone <your-instance-repo-url> ~/brain
cd ~/brain && ./bootstrap.sh
# then personalize people/me.md
```

`bootstrap.sh` is idempotent. It (1) symlinks each skill in `install/skills/`
into `~/.claude/skills/`, and (2) appends the `install/claude-md-snippet.md`
block (with this vault's path interpolated) to `~/.claude/CLAUDE.md`, so the
brain becomes ambient in every session. Re-running it is safe.

Manual equivalent (no shell / Windows — symlinks unavailable, copy instead):
1. Copy `install/skills/{remember,recall,lint}` into `~/.claude/skills/`.
2. Append `install/claude-md-snippet.md` to `~/.claude/CLAUDE.md`, replacing
   `__VAULT_DIR__` with this repo's absolute path.

## Using this from other harnesses

The vault is plain markdown in git, so it is harness-agnostic:

- **Any agent (Codex, Cursor, etc.):** point it at this repo and say "read
  `AGENTS.md` and `index.md`, then recall X." The rules live in the repo, not
  only in the Claude Code skills.
- **Claude.ai web / mobile app (read-only):** add the GitHub connector, point it
  at this repo, ask it to read `AGENTS.md` + `index.md` and recall. Writes from
  mobile are out of scope — draft in chat, let Claude Code commit later.

## Swapping the remote

The git remote is a one-line change — nothing here binds to GitHub except the
mobile connector convenience:

```bash
git remote set-url origin <gitea|codeberg|self-hosted-url>
```

Self-hosted Gitea/Forgejo keeps every property above; Syncthing (P2P, no vendor)
works too if you sync the tree and avoid concurrent `.git` writes.
