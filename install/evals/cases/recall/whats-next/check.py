# "What's next" is a normal daily pass: ## Now only, from tasks.md.
from evalkit import *
o = out()
expect("questionnaire" in o, "answer misses a ## Now item (Acme questionnaire)")
expect("hooli" in o, "answer misses a ## Now item (Hooli SSO addendum)")
expect("passport" not in o, "answer pulls in ## Personal on a plain 'what's next'")
expect("lead scoring" not in o, "answer pulls in ## Later on a plain 'what's next'")
expect(vault_unchanged(), "recall changed the vault")
done()
