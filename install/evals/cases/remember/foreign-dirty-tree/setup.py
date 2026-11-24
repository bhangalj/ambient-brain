# Another session's in-flight work: one modified tracked file, one untracked file.
with open("topics/acme-security-review.md", "a") as f:
    f.write("\nDRAFT-IN-FLIGHT: another session is still editing this line.\n")
with open("topics/half-written.md", "w") as f:
    f.write("---\ntype: topic\nupdated: 2026-10-12\n---\n# Half written by another session\n")
