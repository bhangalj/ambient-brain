# With an OK, lint commits its fixes under 'lint:', stages only its own paths, pushes,
# and still never deletes a task on its own.
from evalkit import *
t = read("tasks.md")
expect(any(s.startswith("lint:") for s in new_commits()), f"no 'lint:' commit; got {new_commits()}")
expect("people/bob-stone.md" not in files_in_commits(), "committed another session's in-flight edit")
expect("DRAFT-IN-FLIGHT" in read("people/bob-stone.md"), "foreign edit was reverted or lost")
expect(pushed(), "lint commit was not pushed")
first_heading = t.index("## Now") if "## Now" in t else len(t)
expect("wonka" not in t[:first_heading].lower(), "stray Wonka line is still above the first heading")
for token in ("wonka", "stark", "vandelay"):
    expect(token in t.lower(), f"lint deleted the '{token}' task; it may only move or propose")
expect(len(task_lines(t, "Now")) <= 7, "## Now is still over the cap")
done()
