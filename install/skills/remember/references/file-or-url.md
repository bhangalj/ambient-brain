# File or URL

Use this file for a filesystem path (PDF, DOCX, PPTX, XLSX, image) or a URL.
Do steps 1 to 5 in order. Then go back to the skill's `SKILL.md` step 4.

1. A meeting transcript the vault owner did not record → write nothing and stop
   (`transcript.md` step 1).
2. Get clean text:
   - File → parse it to text with your document-extraction tool of choice.
   - URL → fetch the page (WebFetch in Claude Code, or your harness's fetch tool).
3. Write the text to `sources/YYYY-MM-DD-<slug>.md`. Redact it (the skill's `SKILL.md`
   step 1) before you write.
4. Distill it:
   - A meeting transcript → do `transcript.md` (this folder) from step 4.
   - Anything else → write the facts to entity pages (the skill's `SKILL.md` step 2).
     A project page gets a `## Log` line at the top, and `## State` or
     `## Decisions` edits when standing state changes.
5. Does it name something the user must do, has finished, or waits on? → also
   do `task-change.md` (this folder).
