---
type: meta
updated: 2026-01-01
---
# AGENTS.md — how to read and write this brain

This is a portable, git-backed **markdown memory vault** — an "ambient brain."
It holds durable, cross-session context: people, projects, durable knowledge,
and the meetings/emails/files worth keeping. **This repo is the single source
of truth** — nothing durable lives outside it. It is markdown, plus the
occasional structured companion file alongside a project doc — still no
runtime, no database, no API key. Any agent or harness that can read files can
use it.

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
| `tasks.md` | open action items by horizon (Now / Next / Blocked / Later / Personal) — the ONLY mutable task state; done = delete the line |
| `people/<slug>.md` | one page per person |
| `projects/<slug>/_project.md` | one page per project (state + docs hub) |
| `projects/<slug>/<name>.data.yml` | structured companion data for a project doc — the markdown stays the narrative |
| `topics/<slug>.md` | durable concepts, facts, reference, ideas |
| `<section>/_index.md` | shard hub — catalogs one section's pages so `index.md` stays one line |
| `meetings/YYYY-MM-DD-<slug>.md` | cleaned, wiki-linked meeting notes |
| `sources/` | raw, **immutable** dropped-in material you ingest FROM |
| `install/` | the skills + global-CLAUDE.md snippet + `bootstrap.sh` (setup glue) |

## Conventions

- **Frontmatter on every note.** Base keys: `type`, `updated` (`YYYY-MM-DD`),
  plus per-type keys below. Use `people:` / `projects:` arrays of wikilinks.
- **`people:` means RELEVANT, not PRESENT.** It is the link graph for the note:
  everyone the note concerns, whether they attended, were discussed, or are named
  in an action item. On a meeting note it is **not** an attendee list — a 1:1 can
  legitimately name ten people. **Attendance lives in the transcript's
  `## Participants` block** (fall back to its speaker labels: chat-app huddles
  often log only the recorder). Anything that asserts someone was in the room —
  above all the `## Meetings` list on a person page — must be built from that
  block, never from `people:`. Getting this backwards once put dozens of meetings
  on the pages of people who never attended them. Where a person page cites a
  meeting they were only discussed in, annotate it `(mentioned, not present)`.
- **Ad-hoc calls have no attendee list, and that is not evidence of absence.**
  A meeting recorder names only the recording's host; on a call with **no
  calendar event** — chat-app huddles, ad-hoc calls — every other speaker comes
  back as `Speaker 1` and the invitee list contains only the vault owner. The
  correlation was verified against the recorder's API: nearly every
  generic-speaker transcript has exactly one invitee. Re-fetching does NOT
  recover the names. **Do not read a solo invitee list as proof someone was
  absent, and do not annotate those entries `(mentioned, not present)`** — the
  counterpart is usually identified by the meeting title, which the recorder
  sets to their name. `/lint` should report these as unverifiable and move on,
  not as violations.
- **Alias-link every person/project on FIRST use per page:** `[[people/jane-doe|Jane]]`,
  `[[projects/acme/_project|Acme]]`. This is the link graph — don't skip it. Later
  bare mentions on the same page are fine and keep prose readable; `/lint` only
  flags a page that never links an entity it names. **Where two people share a
  first name, alias-link each of them on their own first use** — if the vault holds
  a `[[people/jane-doe|Jane]]` and a `[[people/jane-smith|Jane]]`, a bare "Jane"
  after only one is linked is genuinely ambiguous. Never link a same-named
  outsider to a colleague's page.
  **Exception — `_index.md` catalog hubs.** Link people in a hook where it aids
  scanning, but a bare name there is not a lint finding: the entry already links
  its own page, which carries the person links. Linking every name in a 100+ entry
  catalog duplicates the graph and bloats a hub that is read for orientation.
- **Kebab-case slugs that NEVER change.** Slugs are identity; renaming breaks
  every wikilink and every agent's memory of the vault.
- **Structured companion data (`<name>.data.yml`).** When a project doc needs
  an external reader (a script, a rendered sheet) to consume numbers, split
  it: the `.data.yml` holds the structured records — one block per record,
  same fields every time — and the markdown page stays the narrative.
  **Nothing computable is stored** — derive it in the consumer, don't
  hand-type it twice. The rule came from a real miss: a monthly cost was
  hand-typed next to the rate band it derives from, the two disagreed, and
  nothing caught it because the figure and its band were both just stored.
  **This matters for `/remember`:** when new data for such a project arrives,
  the numbers go in the `.data.yml`, not into new markdown tables — a handful of
  hand-maintained tables in one page drifted into eleven contradictions before
  being retired.
- **Drafting anything in the vault owner's voice → read
  [[topics/communication-style]] FIRST.** Emails, chat, DMs, PR descriptions, doc
  prose, review comments — anything going out under their name. That page is
  measured from their own messages and it is the source of truth. **Deliberately
  NOT a skill** — skills fire only in Claude Code, and this vault is meant to work
  for any agent that can read files, so the pointer lives here instead. **Do not
  `@`-inline that page anywhere** — it is large and would load into every session
  for a job that comes up in maybe one turn in ten. A pointer is the right weight,
  which is the same reason `index.md` is capped.
- **Dates are `YYYY-MM-DD`. Encoding is UTF-8.**
- **Meeting ingest = own recordings only.** When ingesting from a meeting
  recorder, ingest only meetings **recorded by the vault owner**. Skip meetings
  that are merely shared/accessible but recorded by someone else (e.g. field or
  customer calls recorded by colleagues), even when they touch relevant
  accounts — those belong to their recorder's memory, not this vault. Raw
  transcripts land in `sources/transcripts/YYYY-MM-DD/<recording_id>_<slug>.md`.
- **Tasks: log vs state.** Meeting notes are the immutable *log* of action
  items (all owners, never retro-edited to track completion); `tasks.md` is the
  mutable *state* — the user's currently-open items only. `/remember` appends
  new user-owned items and **deletes** finished ones (git history is the
  archive); `/recall` answers "outstanding tasks" from `tasks.md` alone.
  Starting empty is fine — declare task bankruptcy explicitly; anything still
  relevant will resurface.
- **Tasks: what earns a line.** `tasks.md` is for **material work the vault owner
  still has to do** — something with a real outcome that needs building, deciding,
  or a conversation with a named person. It is not a checklist of the mechanical
  steps inside work already underway. Adding a line is a claim on their attention;
  the bar is "would they be annoyed to find this had NOT been done", not "is this a
  thing that could be done."

  **Never create a task for:**
  - **Mechanical steps inside work already in flight** — commit this, push that,
    merge the PR, bump a version, update the doc you just edited. Those are part
    of doing the thing. If the work matters, the work is the task.
  - **Verifying your own recent change** — "confirm the deploy landed", "check
    the fix worked". Either verify it now, or state plainly on the project page
    that it is unverified. Parking it as a task pushes a 30-second check into
    someone's backlog.
  - **Passive watching** — "watch X in case it breaks". Either wire an alert or
    accept the risk and say so. A human cannot execute "keep an eye on it."
  - **Looking up a fact you could look up now.** Go and look.
  - **Restating that a project exists.** The project page already tracks it; a
    task line duplicates it and the two then drift apart.

  **Do create a task for:** work blocking someone else, anything with a date,
  anything needing a decision only the vault owner can make, an explicit chase
  (`(waiting on X — asked YYYY-MM-DD)`, filed under `## Blocked`), and work
  that would otherwise be forgotten because no project page owns it.

  **When in doubt, write it on the project page, not here.** A project page
  carries unbounded detail and rots gracefully; `tasks.md` is read as a list of
  things to act on this week, so a stale line there costs more than a stale
  paragraph anywhere else. **This cuts both ways on ingest:** be as willing to
  DELETE a line the input shows is finished as to add a new one.
- **Tasks: line format.** One line per **open** item:
  `- **<task>** … — [[meetings/YYYY-MM-DD-<slug>|src]] (YYYY-MM-DD)`.
  The trailing date is the **capture** date, not a deadline. Done = **delete the
  line** (git history is the archive — no checkboxes, no done-section).
- **Tasks: sections — the horizon convention.** `tasks.md` holds open items
  under exactly five headings, **in this order: `## Now`, `## Next`,
  `## Blocked`, `## Later`, `## Personal`.** No task line ever sits outside one
  of them (not in the header blockquote, not before the first heading). Route
  by **horizon**, not by domain:
  1. **`## Now`** — hard cap **7 items**. A task belongs here only if it has a
     real deadline within about two weeks, or another named person is blocked
     waiting on it. Sorted soonest-deadline first. This is the only section
     read in a normal daily pass. When an eighth item qualifies, demote or
     delete one to stay at 7.
  2. **`## Next`** — actionable now, but no date pressure. Sorted
     newest-capture first.
  3. **`## Blocked`** — cannot progress because a named person or vendor owes
     something. Every line MUST carry `(waiting on <name>)`. Sorted newest
     first. Blocked work is not actionable, so it should not sit in the
     sections you read to decide what to do next.
  4. **`## Later`** — a quarter out or beyond, or genuinely no urgency.
     Explicitly NOT read in a normal pass. Sorted newest first.
  5. **`## Personal`** — life outside work (property, personal finance, health,
     family, personal admin). Flat list, newest first, unchanged by this scheme.
     Domain beats horizon here: a personal item stays in `## Personal`
     regardless of date pressure — it does not move to `## Now` for acquiring a
     deadline. This holds whatever the task's shape — a personal research task
     or a personal side-project code change still belongs here (e.g. work under
     `projects/<personal-project>/_project`). When a task is genuinely both (a
     personal matter handled on work time), it is Personal.

  **The Now cap and the expiry rule.** `/lint` enforces the 7-item cap on
  `## Now` and `/remember` must respect it when filing. `/lint` also flags any
  line in `## Next` or `## Later` whose capture date is more than 21 days old
  and has no deadline; each flagged line must be given a deadline, demoted to
  `## Later`, or deleted. `/lint` PROPOSES, the vault owner decides — `/lint`
  never deletes a task on its own.

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
Optional chat keys let an agent read a person's DM or find their messages
without asking for an ID — it's on the page. Keep the keys generic to whichever
chat tool you use, and record its gotchas (deactivated accounts, external guest
users, pagination) on a `topics/` page rather than here.
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

**Sharding a section — the `_index` hub pattern.** When a section outgrows a
screen, move its per-page lines into a `<section>/_index.md` catalog and leave
`index.md` pointing at just that one hub (`people/`, `topics/`, and `meetings/`
are the usual candidates). Rules:
- The catalog hub is `type: meta` and holds the same one-line-per-page list,
  where the strict ≤80 cap relaxes (it's one hop deeper, not loaded every
  session) — so keep the fuller, more useful hook here.
- `index.md`'s pointer line stays **generic** — no page counts, date ranges, or
  other facts that rot as pages are added (e.g. "durable concepts, reference &
  ideas (sharded)", never "40 topics"). The count-bearing summary, if any, lives
  in the hub, not the index.
- A hub that also carries real prose/content (not just a catalog) is a **content
  hub** and stays `type: topic` — e.g. `topics/<big-topic>/_index.md`, which
  splits one big topic into a directory of leaf pages. Leaf pages back-link their
  hub; `index.md` links only the hub, never the leaves.

## Never store (hard rule)

This vault is a private git repo that pushes off-device; git history is
permanent. **Never store:** secrets, credentials, API keys, tokens, `.env`
contents, or regulated/customer PII you did not deliberately choose to keep.

On ingest, `/remember` redacts these secret patterns before writing to
`sources/` — this is the **canonical redaction list**; `/remember` and `/lint`
reference it rather than re-enumerating, so add new patterns here only:
`sk-[A-Za-z0-9]{20,}`, `gho_[A-Za-z0-9]+`, `AKIA[0-9A-Z]{16}`,
`Bearer [A-Za-z0-9._-]+`, and anything password/token-shaped.
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
into `~/.claude/skills/`, (2) appends the `install/claude-md-snippet.md` block
(with this vault's path interpolated) to `~/.claude/CLAUDE.md` so the brain
becomes ambient in every session, (3) pins this repo's git auth to the repo
owner so a multi-account machine always pushes as the right identity, and
(4) installs the optional meeting auto-ingest LaunchAgent and its session-start
hook — **only** when run as `./bootstrap.sh --with-fathom`; skipped by default.
Re-running it is safe.

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

**Local-only** is also supported: a vault with no remote at all. `/remember`
and `/lint` detect this (`git remote` prints nothing) and commit locally
without pull or push. The trade-off is no off-device copy.

Self-hosted Gitea/Forgejo keeps every property above; Syncthing (P2P, no vendor)
works too if you sync the tree and avoid concurrent `.git` writes.

## Git auth on multi-account machines

`gh`'s credential helper serves only the ACTIVE account's token, so a vault push
from a session where a different GitHub account is active fails with
"repository not found". The durable fix (applied by `bootstrap.sh` step 3,
idempotent) is a **repo-local** credential helper in this repo's `.git/config`
that always answers with the vault owner's token from gh's keyring — the owner
is parsed from the origin URL, and the owner must be `gh auth login`-ed once on
the machine. `/remember` and `/lint` preflight with
`git -C <vault> ls-remote -q origin HEAD` before pushing and point back to
`bootstrap.sh` on failure. Never repair a push failure with `gh auth switch`:
it flips global state and races parallel sessions. Non-GitHub or SSH remotes
skip all of this (the helper is inert there).
