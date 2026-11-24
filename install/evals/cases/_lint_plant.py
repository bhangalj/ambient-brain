# Shared by the lint cases: plants one instance of each problem the lint must find.
import os, re
t = open("tasks.md").read()
anchor = '> Later, Personal (see AGENTS.md → "Tasks: sections").\n'
assert anchor in t
t = t.replace(anchor, anchor + "- **Chase the stray Wonka invoice** (2026-10-09)\n")
t = t.replace("## Blocked\n", "## Blocked\n- **Get the Vandelay logo files from marketing** (2026-10-09)\n")
t = t.replace("## Next\n", "- **Prep the Stark QBR agenda** — due 2026-10-24 (2026-10-08)\n\n## Next\n")
open("tasks.md", "w").write(t)
d = "sources/transcripts/2026-10-03"
os.makedirs(d, exist_ok=True)
open(f"{d}/222_it-huddle.md", "w").write("# IT huddle\nPrinter is broken again.\n")
open(f"{d}/333_globex-discovery.md", "w").write("# Globex discovery call\nThey want SSO and EU hosting.\n")
with open("sources/transcripts/SKIPPED.md", "a") as f:
    f.write("\n- `2026-10-03/222_it-huddle.md` — low-value IT huddle (2026-10-04)\n")
# 76 characters, 82 bytes: must NOT be flagged as over the 80-char cap.
line = "- [[topics/_index]] — durable concepts → reference · ideas · notes (sharded)"
s = open("index.md").read().replace(
    "- [[topics/_index]] — durable concepts, reference & ideas (sharded)", line)
open("index.md", "w").write(s)
import subprocess
subprocess.run(["git", "add", "-A"], check=True)
subprocess.run(["git", "commit", "-q", "-m", "plant lint findings"], check=True)
subprocess.run(["git", "push", "-q"], check=True)
