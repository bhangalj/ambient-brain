# Stage only this run's paths. Foreign changes stay uncommitted and untouched.
from evalkit import *
expect("head of data platform" in read("people/bob-stone.md").lower(),
       "people/bob-stone.md does not record the new manager")
changed = files_in_commits()
for foreign in ("topics/acme-security-review.md", "topics/half-written.md"):
    expect(foreign not in changed, f"committed another session's file: {foreign}")
expect("DRAFT-IN-FLIGHT" in read("topics/acme-security-review.md"), "foreign edit was reverted or lost")
expect(read("topics/half-written.md") != "", "foreign untracked file was deleted")
expect(pushed(), "commit was not pushed to origin")
done()
