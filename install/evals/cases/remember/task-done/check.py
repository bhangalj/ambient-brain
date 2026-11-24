# Finished = delete the line. No checkbox, no "done" marker, no archive section.
from evalkit import *
t = read("tasks.md")
expect("questionnaire" not in t.lower(), "the finished task line is still in tasks.md")
expect("[x]" not in t.lower() and "## done" not in t.lower(), "task was marked done instead of deleted")
expect(len(task_lines(t, "Now")) == 6, f"## Now should hold 6 lines, holds {len(task_lines(t, 'Now'))}")
expect("questionnaire" in read("meetings/2026-10-01-acme-kickoff.md").lower(),
       "the meeting note's action-item log was edited (it is immutable)")
done()
