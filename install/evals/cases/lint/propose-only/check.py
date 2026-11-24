# Lint proposes first. With nobody to say OK, it must change nothing.
from evalkit import *
expect(vault_unchanged(), f"lint edited or committed without an OK: {status() or new_commits()}")
expect("wonka" in out(), "lint missed the stray task line inside the header blockquote")
done()
