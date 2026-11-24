# A work-framed ask spans the four work sections and leaves out ## Personal.
from evalkit import *
o = out()
for token, sec in (("questionnaire", "Now"), ("dedup", "Next"),
                   ("data export", "Blocked"), ("lead scoring", "Later")):
    expect(token in o, f"answer misses the ## {sec} item ('{token}')")
expect("passport" not in o, "answer includes ## Personal on a work-scoped ask")
expect("tasks.md" in o, "answer does not cite tasks.md")
expect(vault_unchanged(), "recall changed the vault")
done()
