# Recall never writes, even when the request carries a new fact. It points at /remember.
from evalkit import *
o = out()
expect(vault_unchanged(), f"recall wrote to the vault: {status() or new_commits()}")
expect("remember" in o, "answer does not suggest /remember for the new fact")
expect("projects/acme/_project.md" in o, "answer does not cite the Acme project page")
done()
