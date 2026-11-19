---
type: meta
updated: 2026-01-01
---
# AGENTS.md — how to read and write this brain

This is a portable, git-backed **markdown memory vault** — an "ambient brain." It holds durable, cross-session context: people,
projects, durable knowledge, and the meetings/emails/files worth keeping. **This repo is the single source of truth** — every durable fact
lives here. It is markdown, plus the occasional structured companion file alongside a project doc — still no runtime, no database,
no API key. Any agent or harness that can read files can use it.

## The three verbs

- **remember** — ingest something: preserve the raw in `sources/` (if it's a real source), distill it into the right entity page, update
  `index.md`, commit + push. (`/remember` skill.)
- **recall** — look something up: read `index.md` → the entity page → depth. Read-only, always cited. (`/recall` skill.)
- **lint** — reconcile: contradictions, stale claims, orphans, missing cross-refs, undistilled sources, index-cap. Proposes, commits on
  OK. (`/lint` skill.)

Optional, Claude Code only: **retro** mines recent session transcripts for repeated corrections and errors, and proposes rule, skill
and topic edits. Applies only what the user approves. (`/retro` skill, `install/retro/extract.py`.)

## Answering "what do I know about X?"

Read in this order; stop as soon as you have enough:

1. **`index.md`** — the map of the whole brain (loaded into every session).
2. **The entity page** — `people/<slug>.md`, `projects/<slug>/_project.md`, `topics/<slug>.md`, or `meetings/YYYY-MM-DD-<slug>.md`.
3. **Depth** — follow wikilinks between entity pages.
4. **Raw** — `sources/` holds the immutable original (transcript, email, parsed file) a page was distilled from. Re-read it to
   re-distill or verify.

## Layout

| Path | Holds |
|---|---|
| `AGENTS.md` | this file — THE agent entry point |
| `index.md` | one-line-per-page map of the brain; loaded every session; capped |
| `tasks.md` | open action items by horizon (Now / Next / Blocked / Later / Personal) — the ONLY mutable task state; done = delete the line |
| `people/<slug>.md` | one page per person |
| `projects/<slug>/_project.md` | one page per project (state + docs hub) |
| `projects/<slug>/<name>.data.yml` | structured companion data for a project doc — the markdown stays the narrative |
| `topics/<slug>.md` | durable concepts, facts, reference, ideas |
| `<section>/_index.md` | shard hub — catalogs one section's pages so `index.md` stays one line |
| `meetings/YYYY-MM-DD-<slug>.md` | cleaned, wiki-linked meeting notes |
| `sources/` | raw, **immutable** dropped-in material you ingest FROM |
| `install/` | the skills + the global-CLAUDE.md snippet |
| `install/retro/` | `extract.py`: mines Claude Code transcripts into a retro digest; the digest stays in `.git/retro/`, never the tree |
| `bootstrap.sh` | setup glue: links the skills, adds the snippet, pins git auth |

## Conventions

- **Frontmatter on every note.** Base keys: `type`, `updated` (`YYYY-MM-DD`), plus per-type keys below. Use `people:` / `projects:`
  arrays of wikilinks.
- **`people:` means RELEVANT, not PRESENT — attendance comes only from the transcript.** `people:` is the link graph (everyone the note
  concerns), not an attendee list — a 1:1 can legitimately name ten people. Anything asserting someone was *in the room* — above all a
  person page's `## Meetings` list — must be built from the transcript. Three cases:
  - A recorder's or calendar's participant list proves **invitation, not presence** — it comes from the invite list, no-shows
    included. Corroborate against speaker turns before asserting attendance; where an invitee didn't speak, say why.
    Annotate `(invited, not present — <reason>)` when the reason is known, else `(invited, did not speak)` — and word the hook as an
    invitation. Silence alone isn't proof of absence — it's a prompt to check.
  - No-calendar calls (huddles, ad-hoc) have **no attendee list at all** — the recorder names only the host; other speakers show as
    `Speaker 1` and re-fetching won't recover names. Identify the counterpart from the meeting title. A solo invitee proves nothing
    about who else attended, so leave attendance unannotated. `/lint` reports these unverifiable, not violations.
  - Discussed-but-absent: annotate `(mentioned, not present)`.
- **Alias-link every person/project on FIRST use per page:** `[[people/jane-doe|Jane]]`, `[[projects/acme/_project|Acme]]`. Builds the
  link graph; later bare mentions on the same page are fine. `/lint` only flags a page that never links an entity it names. Same first
  name → alias each on its own first use (`[[people/jane-doe|Jane]]` and `[[people/jane-smith|Jane]]`). Link a same-named outsider
  only to their own page. **Exempt:** `_index.md` catalog hubs and a person page's `## Meetings` log — citations, not graph-building
  prose, since the linked entry/note already carries the link — and `people/me` (the owner is implicit on their own vault).
- **Kebab-case slugs that NEVER change.** Slugs are identity; renaming breaks every wikilink and every agent's memory of the vault.
- **Structured companion data (`<name>.data.yml`).** When a project doc needs an external reader (script, rendered sheet) to consume
  numbers, split it: the `.data.yml` holds the structured records (one block per record, same fields every time), the markdown page
  stays narrative. **Nothing computable is stored** — derive it in the consumer. A figure hand-typed next to the rate it derives from
  drifts, and nothing catches it while both are just stored. **For `/remember`:** new data for such a project goes in the `.data.yml`.
- **Drafting anything in the vault owner's voice → read their style page FIRST, if they keep one** (`topics/my-communication-style.md`,
  measured from a real sample of their own sent messages). Emails, chat, DMs, PR descriptions, doc prose, review comments — anything
  going out under their name. Deliberately not a skill (must work for any agent that reads files) and not `@`-inlined here (large,
  would load every session for a rare job) — a pointer is the right weight, same reasoning as the index cap.
- **Dates are `YYYY-MM-DD`. Encoding is UTF-8.**
- **No snapshot counts.** Keep a number only when it drives a decision or IS the finding (a threshold, a price, a quota, "422 of
  709 leads skipped the form"). Point-in-time tallies, inventory counts and installed versions rot and nobody acts on them:
  `/remember` leaves them out; `/lint` flags them.
- **Meeting ingest = own recordings only.** Where a recorder holds other people's meetings, ingest only those **recorded by the vault
  owner**. A meeting someone else recorded (e.g. a colleague's field/customer call) belongs to its recorder's memory, even on a
  relevant account. Raw transcripts land in `sources/`.
- **Tasks: log vs state.** Meeting notes are the immutable *log* of action items (all owners, never retro-edited to track completion);
  `tasks.md` is the mutable *state* — the user's currently-open items only. `/remember` appends new user-owned items and **deletes**
  finished ones (git history is the archive); `/recall` answers "outstanding tasks" from `tasks.md` alone. Starting empty is fine —
  declare task bankruptcy explicitly; anything still relevant will resurface.
- **Tasks: what earns a line.** For **material work the vault owner still has to do** — a real outcome needing building, deciding, or a
  conversation with a named person. Bar: "would they be annoyed to find this had NOT been done".
  - **Never:** mechanical steps in in-flight work (commit, push, merge, bump, update the doc you just edited — the work is the task);
    verifying your own recent change (verify now, or say plainly on the project page it's unverified); passive watching (wire an alert
    or accept the risk, don't "keep an eye on it"); a fact you could look up now (go look); restating that a project exists (its page
    already tracks it); work gated on something not yet true, such as a wiki nobody has adopted (note it on the project page);
    reactive work done when it comes up, where the vault already holds the how-to (a delivery note when the order arrives); work that
    is someone else's job (another person's tool, process or rollout); a question or pitch that may go nowhere ("ask whether they
    still need X", "train a team on tool Y"); a step that sits in a project plan already. One outcome is one line: fold sub-steps
    into it.
  - **Do:** work blocking someone else; anything with a date; a decision only the owner can make; an explicit chase (`(waiting on X —
    asked YYYY-MM-DD)`, filed under `## Blocked`); work with no project page to own it.
  - **Says what REMAINS** — `tasks.md` is read to decide what's next, so completion lives in the project's `## Log`. Binds
    `/remember`: rewrite a part-done line to what remains ("X is SHIPPED, what remains is Y" → "Y") or delete it; link the detail
    page for evidence: `- **Do Y** — [[projects/foo/_project|src]] (YYYY-MM-DD)`.
  - **When in doubt, write it on the project page** — a stale task line costs more than a stale paragraph elsewhere. Delete a
    finished line as readily as you add a new one.
- **Tasks: line format.** One line per **open** item: `- **<task>** … — [[<src>|src]] (YYYY-MM-DD)`, where `<src>` is the source note
  or the project page. The trailing date is the **capture** date, not a deadline. Done = **delete the line** (no checkboxes, no
  done-section).
- **Tasks: sections — the horizon convention.** Exactly five headings, in this order, and every line sits under one: `## Now`, `## Next`,
  `## Blocked`, `## Later`, `## Personal`. Route by **horizon**:
  - **`## Now`** — cap **7**. Only a real deadline within ~2 weeks, or another named person blocked waiting. Soonest-deadline first; the
    only section read daily. An 8th item bumps one out.
  - **`## Next`** — actionable, no date pressure. Newest-capture first.
  - **`## Blocked`** — stalled on a named person/vendor; every line MUST carry `(waiting on <name>)`. Newest first; not read when
    deciding what's next.
  - **`## Later`** — a quarter or more away, or no urgency. Not read in a normal pass. Newest first.
  - **`## Personal`** — life outside work (home, personal finance, health, family, admin). Flat, newest first. Domain beats horizon:
    stays here regardless of deadline, whatever its shape — a personal research task or side-project code change included. Genuinely
    both → Personal.
  - **Cap + expiry.** `/lint` enforces the `## Now` cap of 7; `/remember` must respect it when filing. `/lint` flags any `## Next`/`##
    Later` line whose capture date is >21 days old with no deadline — give it a deadline, demote it, or delete it. `/lint` PROPOSES,
    the vault owner decides — never deletes a task itself.

Entity schemas:

```yaml
# people/<slug>.md
---
type: person
name: Jane Doe
chat_id: U0123ABCD        # optional — chat-app user ID
chat_handle: jane.doe     # optional
chat_dm: D0123ABCD        # optional — the 1:1 DM channel with the vault owner
updated: 2026-01-01
---
```
Optional chat keys let an agent read a person's DM or find their messages without asking for an ID — it's on the page. Keep the keys
generic to whichever chat tool you use, and record its gotchas (deactivated accounts, external guest users, pagination) on a
`topics/` page rather than here.
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
# projects/<slug>/<doc>.md — any non-hub doc inside a project folder
---
type: project-doc
project: "[[projects/<slug>/_project]]"
updated: 2026-01-01
people: ["[[people/jane-doe]]"]   # optional
---
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

`index.md` loads into EVERY session, so it must stay lean: **one terse line per entity page, ≤ ~80 characters** (name + hook). Depth
lives one file deeper. `/lint` enforces this — trimming over-long lines, de-duping, and sharding/archiving any section that outgrows a
screen.

**Sharding — the `_index` hub pattern.** When a section outgrows a screen, move its lines into `<section>/_index.md` and point
`index.md` at just that hub (`people/`, `projects/`, `topics/`, `meetings/` are the usual candidates):
- The hub is `type: meta`, holds the same one-line-per-page list, and the ≤80 cap relaxes there (one hop deeper, not loaded every
  session) — keep the fuller hook.
- `index.md`'s pointer line stays **generic**: a name and a hook, no counts (e.g. "durable concepts, reference & ideas (sharded)").
- A hub with real prose (not just a catalog) is a **content hub** and stays `type: topic` — e.g. `topics/<big-topic>/_index.md`, which
  splits one big topic into a directory of leaf pages. Leaf pages back-link their hub; `index.md` links only the hub.

## Never store (hard rule)

This vault is a private git repo that pushes off-device; git history is permanent. **Never store:** secrets, credentials, API keys,
tokens, `.env` contents, or regulated/customer PII you did not deliberately choose to keep.

On ingest, `/remember` redacts these secret patterns before writing to `sources/` — this is the **canonical redaction list**;
`/remember` and `/lint` reference it rather than re-enumerating, so add new patterns here only: `sk-[A-Za-z0-9]{20,}`,
`gho_[A-Za-z0-9]+`, `AKIA[0-9A-Z]{16}`, `Bearer [A-Za-z0-9._-]+`, and anything password/token-shaped. If a source is fundamentally a
secret, refuse and tell the user. `/lint` audits for leaks.

## Precedence vs native memory

Durable, cross-session, or personal facts live HERE. Claude Code's native per-project memory (`~/.claude/projects/*/memory/`) is only
for disposable, project-local progress notes.

## Bootstrap — stand this up on a new machine

```bash
git clone <your-instance-repo-url> ~/brain
cd ~/brain && ./bootstrap.sh
# then personalize people/me.md
```

`bootstrap.sh` is idempotent. It (1) symlinks each skill in `install/skills/` into `~/.claude/skills/`, (2) appends the
`install/claude-md-snippet.md` block (with this vault's path interpolated) to `~/.claude/CLAUDE.md` so the brain is ambient in every
session, and (3) pins this repo's git auth to the repo owner so a multi-account machine always pushes as the right identity. Skills
run straight from the vault, so a `git pull` updates them. Re-running is safe.

Manual equivalent (no shell / Windows — symlinks unavailable): copy `install/skills/{remember,recall,lint,retro}` into `~/.claude/skills/`
and append `install/claude-md-snippet.md` to `~/.claude/CLAUDE.md` by hand, replacing `__VAULT_DIR__` with this repo's absolute path.

## Using this from other harnesses

Plain markdown in git — harness-agnostic. **Any agent** (Codex, Cursor, etc.): point it at the repo, "read `AGENTS.md` and `index.md`,
then recall X" — the rules live in the repo, not only in the Claude Code skills. **Claude.ai web/mobile (read-only):** add the GitHub
connector, point it at the repo, ask it to read `AGENTS.md` + `index.md` and recall. Writes from mobile are out of scope — draft in
chat, let Claude Code commit later.

## Swapping the remote

The git remote is a one-line change — nothing here binds to GitHub except the mobile connector convenience:

```bash
git remote set-url origin <gitea|codeberg|self-hosted-url>
```

**Local-only** is also supported: a vault with no remote at all. `/remember` and `/lint` detect this (`git remote` prints nothing) and
commit locally without pull or push. The trade-off is no off-device copy.

Self-hosted Gitea/Forgejo keeps every property above; Syncthing (P2P, no vendor) works too if you sync the tree and avoid concurrent
`.git` writes.

## Git auth on multi-account machines

`gh`'s credential helper serves only the ACTIVE account's token, so a vault push from a session with a different GitHub account active
fails "repository not found". Durable fix (`bootstrap.sh` step 3, idempotent): a **repo-local** credential helper in this repo's
`.git/config` that always answers with the vault owner's token from gh's keyring (owner parsed from the origin URL; must be `gh auth
login`-ed once on the machine). `/remember` and `/lint` preflight with `git -C <vault> ls-remote -q origin HEAD` and point back to
`bootstrap.sh` on failure. **Never repair a push failure with `gh auth switch`:** it flips global state and races parallel sessions.
Non-GitHub or SSH remotes skip all of this (the helper is inert there).
