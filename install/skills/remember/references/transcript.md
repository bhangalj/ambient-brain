# Pasted transcript or long text

Use this file for a meeting transcript from any source (pasted, a file, a
recorder export), and for an email, chat or other long block. Do steps 1 to 9
in order. Then go back to the skill's `SKILL.md` step 4.

## 1. Own recordings only

When a recorder holds other people's meetings, ingest only those the vault
owner recorded. A meeting someone else recorded belongs to that person's
memory, even on a relevant account. Not recorded by the vault owner → write
nothing and stop.

## 2. Save the raw text to `sources/`

Name the file `sources/YYYY-MM-DD-<slug>.md`. Write the text to the file
verbatim, every line to the end. Never summarise or retype it from memory.

Redact once, before you write. Replace every match of the redaction list in the
skill's `SKILL.md` step 1 with `[REDACTED]`. Carry no secret into any other
page. If the text is fundamentally a secret, write nothing and refuse.

The `sources/` file is immutable after this step.

## 3. Read all of it

Read the text to the last line. Facts, dates and action items sit anywhere in
it. A summary at the top does not hold them all.

## 4. Write the meeting note

Not a meeting → skip the rest of step 4 and steps 5 and 6. Distill the text into entity
pages (the skill's `SKILL.md` step 2), then continue at step 7.

Meeting → write `meetings/YYYY-MM-DD-<slug>.md`, dated on the meeting day. Use
a kebab-case slug from the title.

- Frontmatter: `type: meeting`, `date`, `people: [...]`, `project: "[[...]]"`,
  `source: "[[../sources/<file without .md>]]"`, `updated`.
- Body: a one-line TL;DR, thematic `## sections`, then `## Action items` with
  wikilinked owners. List every owner's items here. This is the log.
- Verify each person slug in `people/_index.md` (or the People section of
  `index.md` while unsharded) before you link it. Cross-link every person and
  project.
- Name the meeting this one follows on from, where relevant.

Transcript cautions:

- Speaker labels can be wrong. A recorder may give whole stretches to one
  person, and it may garble proper nouns, including the owner's name. Trust
  the content, not the labels. Gloss garbled names by the work the speaker
  describes, and check them against earlier notes and the people catalog.
- Fake speaker names. A recorder may label an unknown speaker with an invented
  or famous name instead of `Speaker 1`. Compare every speaker name with the
  participant list and the people catalog. A speaker who is neither an invitee
  nor a known person is a fake label. Never link or quote that name. Work out
  who it is from context if you can. Say in the note that the labels are
  unreliable.
- Currency: take each figure's currency from the transcript line, not from a
  generated summary. A summary can render every bare figure in one default
  currency. Write the currency symbol only when a speaker names it or the
  contract is clearly in that currency. A total in one currency over parts in
  another is the usual sign of this error.

## 5. Attendance

A recorder's or calendar's participant list proves invitation, not presence. It
includes no-shows. Attendance comes from the speaker turns. For each person in
any attendee or participant list in the note, and on their page:

1. Spoke → plain entry.
2. Invited, never spoke, reason known (leave, left the company) → append
   `(invited, not present — <reason>)`.
3. Invited, never spoke, no reason known → append `(invited, did not speak)`.
   Word the hook so it does not claim they took part.
4. Only discussed → `(mentioned, not present)`, or leave their page alone.
5. Only generic labels (`Speaker 1`), no invite list → name the counterpart
   from the title. Annotate absence only where you can prove it.
6. Labels look unreliable (one person holds whole stretches, a label is
   neither an invitee nor a known person) → say so in the note. Annotate no
   attendance from those labels.

## 6. Back-link attendees

Add the note to the `## Meetings` list on `people/<slug>.md` for each person
in the attendee list from step 5. Skip `people/me.md`. Put it at the top (newest first) and match the
page's line format.

## 7. Update project and topic pages

Match the content to the hooks in `index.md` and the `_index.md` catalogs where
they exist. For each project or topic page it touches:

- Set `updated:` to today.
- Add a `## Log` line at the top (newest first).
- Edit `## State` or `## Decisions` when a fact changes standing state (a date,
  a commitment, a decision).

A recurring meeting usually maps to the same pages as its earlier notes. Check
their `project:` frontmatter. A durable fact that fits no project goes on the
matching `topics/` page.

## 8. Action items

For each action item the USER owns, do `task-change.md` (this folder). Action items
owned by anyone else stay only in the meeting note.

## 9. Index line

For the index (the skill's `SKILL.md` step 4), add a meeting line to the meetings
catalog: `meetings/_index.md` when it exists, else the Meetings section of
`index.md`. Newest first.
