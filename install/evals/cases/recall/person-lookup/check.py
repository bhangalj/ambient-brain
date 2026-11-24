# Entity lookup through the sharded index, answered with a file-path citation.
from evalkit import *
o = out()
expect("people/jane-doe.md" in o, "answer does not cite people/jane-doe.md")
expect("ciso" in o, "answer misses her role (CISO)")
expect("async" in o or "email" in o, "answer misses her stated preference (async email)")
expect(vault_unchanged(), "recall changed the vault")
done()
