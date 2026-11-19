# Task changes: `<vault>/tasks.md`

Use this file when the input names something the user must do, has finished,
or waits on. `tasks.md` holds only the user's open items. Meeting notes are the
immutable log of action items for all owners: never edit them to track a task.

Do steps 1 to 7 in order. Then go back to the skill's `SKILL.md` step 4.

## 1. Read

Read all of `tasks.md`. It has exactly five headings, in this order: `## Now`,
`## Next`, `## Blocked`, `## Later`, `## Personal`. Count the lines under `## Now`.

## 2. Reconcile the existing lines

Do these three checks before you add anything:

1. Did this input close, advance, contradict or renegotiate an existing line?
   Closed → delete it (step 3). Changed → rewrite it.
2. Is the new item already there? Merge it into that line. Keep the older
   capture date.
3. Is a `## Blocked` line past its own chase date, or waiting on a person this
   input deals with? Put it in the report, even when the input does not mention it.

## 3. Finished or obsolete → delete the line and log it

1. Delete the whole line. Git history is the archive.
2. Finished work that belongs to a project → add a `## Log` line at the top of
   that project's page (newest first) and set its `updated:` to today.
   Completion lives in the project's Log.
3. If the input adds nothing new, stop here and go back to the skill's
   `SKILL.md` step 4.

## 4. Does it earn a line?

The bar: would the user be annoyed to find this had NOT been done? Ask these
questions in order. The first YES or NO decides.

1. Does the user wait on a named person or vendor who owes something (access,
   an answer, a signature, data)? → YES. This is an explicit chase. It always
   earns a line, in `## Blocked`.
2. Is it someone else's job (their tool, process, rollout, or their action
   item from a meeting)? → NO.
3. Is it a mechanical step inside work already in flight (commit, push, merge,
   bump, update the doc you just edited)? → NO. The work is the task.
4. Is it a check of your own recent change? → NO. Verify it now, or say on the
   project page that it is unverified.
5. Is it passive watching ("keep an eye on it")? → NO.
6. Is it a fact you can look up now? → NO. Look it up.
7. Does it only restate that a project exists? → NO.
8. Is it gated on a condition that is not yet true, with nobody to chase (for
   example a wiki nobody has adopted)? → NO.
9. Is it reactive work that the vault already holds the how-to for? → NO.
10. Is it material work with a real outcome (build, decide, a conversation with
    a named person), work that blocks someone else, anything with a date, a
    decision only the user can make, or work with no project page? → YES.
11. Otherwise → NO.

NO → write it on the project page instead. That is the default.

One outcome is one line. Fold sub-steps into it.

## 5. Pick the heading

Ask these questions in order. The first YES decides.

1. Is it life outside work (home, personal finance, health, family,
   personal admin)? → `## Personal`. This holds even with a near
   deadline, and even when the task is research or code. Domain beats horizon.
2. Does the USER wait on a named person or vendor who owes something? →
   `## Blocked`. The line MUST carry `(waiting on <Name>)`.
3. Is there a real deadline within ~2 weeks of today (or already past), OR does
   another named person wait on the USER for it? → `## Now`. Do step 6.
4. Is it a quarter or more away, or with no urgency? → `## Later`.
5. Otherwise → `## Next`. This is the default for a new work task.

Direction matters. Someone waits on the user → `## Now`. The user waits on
someone → `## Blocked`.

## 6. The `## Now` cap is 7

If `## Now` already holds 7 lines, choose ONE of these yourself, in this run:

- a. The new item is more urgent than the least urgent `## Now` line → move
  that line to `## Next` (or delete it if it is no longer real). Then add the
  new item to `## Now`.
- b. Otherwise → put the new item in `## Next`.

Say in the report which you did. `## Now` holds at most 7 lines.

## 7. Write the line

- Format: `- **<task>** … — [[<src>|src]] (YYYY-MM-DD)`. `<src>` is the
  source note or the project page. The trailing date is the CAPTURE date
  (today), not a deadline.
- A `## Blocked` line carries `(waiting on <Name>)`. Wikilink the name
  (`[[people/<slug>|<Name>]]`) only if the vault has a page for the person
  (`people/_index.md`, or `index.md` → People while unsharded).
  Never invent a slug. When the user asked on a known date, write
  `(waiting on <Name> — asked YYYY-MM-DD)`.
- Write what REMAINS to do. Completion goes in the project's `## Log`.
- Sort `## Now` by soonest deadline first. Put a new line at the top of every
  other section (newest capture first).
- Every line sits under one of the five headings.
