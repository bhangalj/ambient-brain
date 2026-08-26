---
type: tasks
updated: 2026-01-01
---
# Tasks — outstanding action items (working set)

> One line per **open** item:
> `- <task> — [[meetings/YYYY-MM-DD-<slug>|src]] (YYYY-MM-DD)`
> The trailing date is the **capture** date, not a deadline.
> Done = **delete the line** (git history is the archive — no checkboxes, no
> done-section). Meeting notes are the immutable log of what was agreed; this
> file is current state only. Maintained by `/remember`, read by `/recall`.
>
> **Five sections, in this order (see AGENTS.md → "Tasks: sections").** Work
> splits by **horizon** — when something matters — not by what kind of work it is.
> A list sorted by capture date buries the thing due tomorrow under the thing you
> happened to write down most recently; sorting by horizon is what makes the file
> skimmable.
> `## Now` — **hard cap 7 items**. Only if it has a real deadline within about two
> weeks, or another named person is blocked waiting on it. Soonest deadline first.
> This is the only section read in a normal daily pass. When an eighth item
> qualifies, one must be demoted to `## Next` or deleted — the cap is the point.
> `## Next` — actionable now, no date pressure. Newest capture first. The default
> for a new task.
> `## Blocked` — cannot progress because a named person or vendor owes something;
> every line carries `(waiting on <name>)`. Newest first. Blocked work is not
> actionable, so it should not sit in the sections you read to decide what to do.
> `## Later` — genuinely no urgency, or a quarter or more away. **Not read** in a
> normal pass.
> `## Personal` — life outside work. Flat list, newest first. Domain beats horizon:
> a personal item stays here regardless of date pressure.
>
> **Expiry rule:** `/lint` flags any line in `## Next` or `## Later` whose capture
> date is more than **21 days** old and which has no deadline. Each flagged line
> must be given a deadline, demoted to `## Later`, or deleted. `/lint` **proposes**;
> you decide — it never deletes a task on its own.

## Now

## Next

## Blocked

## Later

## Personal
