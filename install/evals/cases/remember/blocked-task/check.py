# Waiting on a named person -> ## Blocked, with a (waiting on <name>) tag.
from evalkit import *
t = read("tasks.md")
hits = [l for l in task_lines(t, "Blocked") if "churn" in l.lower()]
expect(hits, "the churn dashboard task is not in ## Blocked")
expect(all("waiting on" in l.lower() and "bob" in l.lower() for l in hits),
       "the ## Blocked line lacks '(waiting on Bob ...)'")
for sec in ("Now", "Next", "Later", "Personal"):
    expect(not any("churn" in l.lower() for l in task_lines(t, sec)), f"task also filed in ## {sec}")
done()
