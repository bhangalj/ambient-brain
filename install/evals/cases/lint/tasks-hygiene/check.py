# tasks.md hygiene: Now over cap, Blocked line with no waiting-on tag, stray line.
import re
from evalkit import *
o = out()
expect("stark" in o, "lint missed the 8th ## Now line (Stark QBR) breaking the cap of 7")
expect("vandelay" in o, "lint missed the ## Blocked line with no '(waiting on <name>)'")
expect("wonka" in o, "lint missed the stray line in the header blockquote")
expect(re.search(r"\bcap\b|\b7\b", o), "lint does not name the ## Now cap")
done()
