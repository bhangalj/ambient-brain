# An invented 72-minute transcript (~13k words) with three planted lines at about
# 5%, 50% and 95% of the body. The recorder summary above the body does not name
# them, so only a full read finds them. Three invitees never speak.
from evalkit import *
import os, re

EARLY = "rebuild the Initech demo environment"
LATE = "sign the renewal early, on 2026-11-20"
LAST_LINE = "Good to have you on."

srcs = [p for p in files_in_commits() if p.startswith("sources/")]
raw = "\n".join(read(p) for p in srcs)
expect(srcs, "the transcript was not saved to sources/")
expect(EARLY in raw and LATE in raw and LAST_LINE in raw,
       "the sources/ copy is not verbatim to the end (a planted line or the last line is missing)")

notes = [p for p in files_in_commits()
         if p.startswith("meetings/2026-10-21") and p.endswith(".md")]
expect(notes, "no meetings/2026-10-21-*.md note was written")
note = "\n".join(read(p) for p in notes)
expect("type: meeting" in note, "the meeting note has no 'type: meeting' frontmatter")

# Late fact: distilled to the project page, not only left in the raw.
expect("2026-11-20" in read("projects/acme/_project.md"),
       "projects/acme/_project.md does not record the 2026-11-20 signature date")

# Mid fact: the user's own action item lands in tasks.md.
t = read("tasks.md")
expect("churn field mapping" in t.lower() or "2026-11-06" in t,
       "the churn field mapping task (the owner's, mid-call) is not in tasks.md")
expect(len(task_lines(t, "Now")) <= 7, f"## Now holds {len(task_lines(t, 'Now'))} lines; the cap is 7")
# Early fact: someone else's action item never goes in tasks.md.
expect("demo environment" not in t.lower(), "Theo's Initech demo task was filed in the user's tasks.md")

# Invited but silent: never listed as an attendee without an annotation.
OK = ("invited", "not present", "did not speak", "absent", "no-show", "silent")
heading = ""
for l in note.splitlines():
    if l.startswith("#"):
        heading = l.lower()
    elif re.search(r"attend|participant|people|present|invite|who", heading) and re.match(r"\s*[-*] ", l):
        for name in ("Priya", "Hannah", "Tomas"):
            expect(name not in l or any(w in l.lower() for w in OK),
                   f"{name} never spoke but is listed as an attendee: {l.strip()}")

expect(pushed(), "commit was not pushed to origin")
expect(status() == "", f"left uncommitted changes: {status()}")
done()
