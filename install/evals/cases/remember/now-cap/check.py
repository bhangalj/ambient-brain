# ## Now already holds 7 lines. An urgent new task must not make it 8.
from evalkit import *
t = read("tasks.md")
now = task_lines(t, "Now")
expect(len(now) <= 7, f"## Now holds {len(now)} lines; the cap is 7")
expect("umbrella" in t.lower(), "the new task was not captured in tasks.md")
o = out()
expect(any(w in o for w in ("demot", "cap", "moved", "next")),
       "report does not say how the cap was handled")
done()
