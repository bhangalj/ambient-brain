# Short fact, person or project update

Use this file for a one-line fact, or a change to a person, project or topic.
Do steps 1 to 5 in order. Then go back to the skill's `SKILL.md` step 4.

1. Write no `sources/` file. Go straight to the entity page.
2. Find the page. Look in each section's `_index.md` catalog where one exists
   (`people/_index.md`, `projects/_index.md`, `topics/_index.md`), else in
   that section of `index.md`.
   - Page exists → edit it in place.
   - No page → create it with the schema in AGENTS.md → "Entity schemas".
3. Write the fact:
   - Person or topic → put the fact in the body. When it replaces an old fact
     (a new office, a new manager), rewrite the old statement. Keep one current
     version.
   - Project → add a `## Log` line at the top (newest first). Edit `## State`
     or `## Decisions` when the fact changes standing state.
4. Set `updated:` to today.
5. Does the input also name something the user must do, has finished, or waits
   on? → also do `task-change.md` (this folder).
