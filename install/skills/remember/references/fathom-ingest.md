# Fathom meeting ingest — playbook

Load this when the input is **"ingest new/latest Fathom meetings"** (or any
Fathom-recording ingestion). It specialises the generic `/remember` steps for
the recurring meeting-ingest pass. General rules in `../SKILL.md` and
`<vault>/AGENTS.md` still apply.

## Tools
**Pull transcripts with the fetcher script, not the MCP.**
`<vault>/sources/fathom-transcripts/fetch_transcripts.py` is the fetcher: **~1
request per 10 meetings** (the list endpoint returns transcript + summary +
action items + highlights inline), `recorded_by` filtered **server-side** so the
own-recordings rule is enforced by the API, written straight to disk instead of
through context. It is **delta by default** (starts from the newest day folder
on disk), skips meetings already fetched, and rebuilds `INDEX.md` from every day
folder — so a narrow run can't truncate it.

`mcp__fathom__*` (all read-only) is for **lookups the script can't do**: resolving
a pasted URL/call-id, or `get_identity` if the owner is unclear. Load with
`ToolSearch → select:mcp__fathom__list_meetings,mcp__fathom__get_identity`.
Don't call `get_meeting_transcript` for a routine ingest — the script already
wrote the file, and pulling it again just burns context.

## 1. Find the delta (what's new since last ingest)
- Read `<vault>/meetings/_index.md` — the top date heading is the last ingested
  day. Also `ls <vault>/sources/fathom-transcripts/` for the day folders present.
- `python3 <vault>/sources/fathom-transcripts/fetch_transcripts.py` with no args
  does the delta itself and prints `N new, M already on disk` plus each new path.
  Full re-pull is `--all` (rate-limits: expect 429 backoff after the first few
  pages); `--force` overwrites in range.
- A meeting already in `meetings/_index.md` **or** present as a file in
  `sources/fathom-transcripts/<date>/` is done — **skip it** (dedup). Transcripts
  on disk are not necessarily distilled: cross-check both lists, don't assume.

## 2. Scope filter — OWN RECORDINGS ONLY
- Ingest only meetings **`recorded by` the vault owner**. Skip anything recorded
  by a colleague even if shared/accessible and even if it touches relevant
  accounts (field/customer calls belong to their recorder's memory).
  This is the AGENTS.md "Fathom ingest = own recordings only" convention.
  The script's `recorded_by[]` filter enforces this — a hand-rolled MCP pull does not.
- If unsure who the owner is, `get_identity` once per session.
- If a borderline meeting is recorded by the owner but you're unsure it's worth a
  full note, read the **`## Summary` / `## Action items` sections at the top of
  the fetched file** and decide — they cost nothing, the script already pulled them.

## 3. Raw files (immutable source) — written by the script
- Path/name is `<vault>/sources/fathom-transcripts/YYYY-MM-DD/<hhmm>_<recording_id>_<slug>.md`
  — **one convention, no hand-named variants** (running two conventions at once
  produces duplicate pairs that then have to be reconciled by hand). Markdown
  only, no `.json` sidecars.
- Each file already carries the metadata header (recording id · type · scheduled/
  recorded times · recorded_by · Fathom + meeting + share URLs), the participant
  list with internal/external tags, Fathom's summary, action items, highlights,
  and the timestamped transcript. Read the file; don't re-pull it.
- Nothing is redacted on write, so **check for secrets in what you read** and
  never lift them into a distilled note (never-store rule).
- **Gotchas:** Fathom often **mislabels speakers** (whole stretches attributed to
  one participant) and mangles proper nouns. Trust the content, not the labels;
  put a speaker-label caveat in the distilled note and gloss the mangled names.
- **Currency: check the transcript, not the summary.** Fathom is a US product and
  its generated `## Summary` silently renders every unqualified figure as
  dollars — a speaker says *"686 in one region and 650 in another"* and the
  summary comes back *"$686k + $650k"*. If your organisation reports in another
  currency, distil bare figures in **that** currency, and write `$` only when a
  speaker actually says "dollars" or the contract is genuinely USD-denominated
  (say so explicitly in the note when it is). Never copy the summary's currency
  symbol without checking the transcript line it came from. This has produced
  real errors: a target distilled as a mixed-unit equation (`$` total over
  non-`$` parts), and a headline number carried across with the wrong symbol —
  each caught only by cross-checking a figure that was already known.

## 4. Distill each → `meetings/YYYY-MM-DD-<slug>.md`
- Slug = kebab of the title (e.g. `weekly-forecast-call`, `acme-kickoff`).
- Frontmatter: `type: meeting`, `date`, `people: [...]`, `project: "[[...]]"`,
  `source: "[[../sources/fathom-transcripts/<date>/<file>]]"`, `updated`.
- House style: a one-line TL;DR/summary, thematic `## sections`, then
  `## Action items` with **wikilinked owners**. Cross-link every person and
  project. **Verify each person slug against `people/_index.md`** before linking
  (don't invent slugs). Note who the meeting follows on from where relevant.

## 5. Propagate to project/topic pages (don't stop at the note)
Don't work from a fixed list of pages — read **`<vault>/index.md`** (the live map
of every project and topic, each with a one-line hook) and route each meeting to
whichever pages its content matches. For every page a meeting touches: bump
`updated:`, add a **`## Log`** line (newest first), and edit **`## State` /
`## Decisions`** when a fact changes standing state (not just recording history).
- Match on the page hooks in `index.md`; a meeting usually hits 1–3 pages.
- A recurring meeting almost always maps to the same page(s) as its prior
  instances — check the earlier note's `project:` frontmatter / `## Log` links.
- Durable non-project facts (a convention, a vendor term, a definition) belong on
  the relevant `topics/*` page, same as any `/remember`.
- If a meeting clearly needs a page that doesn't exist yet, create it per
  AGENTS.md and add its one-line entry to `index.md` (step 7).

## 6. tasks.md — add opens, delete closes
- Append new **user-owned** open items, linked to the meeting src, **under the
  right horizon** (AGENTS.md → "Tasks: sections" — `## Now` / `## Next` /
  `## Blocked` / `## Later` / `## Personal`):
  Ask in this order — the same order `../SKILL.md` step 4 uses:
  - Personal-life items → `## Personal` (bottom, flat list, newest first).
    Domain beats horizon: a personal item stays here even with a near-term
    deadline, whatever its shape.
  - A real deadline inside ~2 weeks, or another named person is blocked
    waiting on it → `## Now`, sorted soonest-deadline first. Respect the
    **hard cap of 7 lines**: if Now is already full, either the new item is
    genuinely more urgent than an existing line (demote that line to `Next`,
    or delete it if it is no longer real) or the new item goes to `Next`
    instead. Say which you did in the report; never silently exceed the cap.
  - Cannot progress because a named person or vendor owes something →
    `## Blocked`, newest first, and the line **must** carry
    `(waiting on <name>)`.
  - A quarter or more away, or genuinely no urgency → `## Later`,
    newest-capture first.
  - Otherwise → `## Next`, newest-capture first — actionable now with no date
    pressure, and the default for a new work task.
- **Delete** any existing line the new meetings resolve — a sync that has now
  happened, a convention confirmed, a task reported done. Git history is the
  archive; no checkboxes, no done-section.

## 7. Indexes
- `meetings/_index.md`: add one line per new meeting under its date heading
  (newest date on top), and **bump the meeting count** in the header.
- `index.md`: touch only if a **new entity page** was created or a project's
  one-liner materially changed (respect the index cap — AGENTS.md).

## 8. Commit + push
Per `../SKILL.md` step 6: preflight `ls-remote`, then stage **only the paths this
run wrote** with an explicit pathspec (never `git add -A` / `git add .` /
`git commit -a`), verify with `git diff --cached --name-only`, then commit /
`pull --rebase` / push, retrying the push once. One commit for the batch is fine.

## Automated path (hourly, unattended)

An optional scheduled runner can drive this same playbook so routine ingest needs
no prompting — for example hourly during working hours via a macOS LaunchAgent
labelled `com.ambient-brain.fathom-autoingest`, active only while the machine is
on. It does **steps 1 and 8 itself** (fetch, and all git), and invokes a headless
`claude -p` for **steps 2–7** with file tools only and no Bash. Distillation
lands on a rolling `fathom-ingest` branch behind a draft PR; raw transcripts go
straight to `main` (the fetcher's delta anchor is the newest day-folder *on
disk*, so raw files must not be stranded on a branch).

Consequences for a **manual** `/remember` run:
- Check `git branch --list fathom-ingest` first. If it exists and is ahead of
  `main`, meetings are already distilled there but unmerged — merge it (or work
  on it) rather than distilling them a second time on `main`.
- The scheduled run defers whenever the working tree is dirty or HEAD is not
  `main`, so it will never collide with a session you are in.

## Fast-path checklist
`_index.md` last date → `python3 sources/fathom-transcripts/fetch_transcripts.py`
(delta, prints the new paths) → drop anything already distilled → read the new
files → meeting notes → project Logs/State → tasks.md (add+delete) →
meetings/_index.md count+lines → commit/push.
