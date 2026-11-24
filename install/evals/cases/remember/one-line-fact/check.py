# A one-line fact goes straight to the entity page: no sources/ file, own commit, pushed.
from evalkit import *
expect("berlin" in read("people/jane-doe.md").lower(), "people/jane-doe.md does not record Berlin")
changed = files_in_commits()
expect(not any(p.startswith("sources/") for p in changed),
       f"a one-line fact created a sources/ file: {sorted(p for p in changed if p.startswith('sources/'))}")
expect(any(s.startswith("remember:") for s in new_commits()), f"no 'remember:' commit; got {new_commits()}")
expect(pushed(), "commit was not pushed to origin")
expect(status() == "", f"left uncommitted changes: {status()}")
done()
