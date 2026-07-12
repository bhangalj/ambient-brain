# ambient-brain (template)

A portable, git-backed, **pure-markdown** memory vault for AI agents — a blank
"second brain" you can use with Claude Code (or any agent that reads files).
Organized Karpathy-style by entity (`people/ projects/ topics/ meetings/`) over
an immutable `sources/` bucket, plus a mutable `tasks.md` working set, with
three skills — `/remember`, `/recall`, `/lint` — and a one-command bootstrap.
No runtime, no database, no API key.

Battle-tested refinements baked in: incremental `/lint` (deep-checks only pages
changed since the last lint commit), the tasks log-vs-state split (meeting notes
are the immutable log; `tasks.md` is current state, done = delete the line), and
a global-rules block managed in-repo and installed by `bootstrap.sh`.

## Use this template

1. Click **Use this template** → create your own **private** repo (e.g. `brain`).
2. Clone it and bootstrap:
   ```bash
   git clone <your-repo-url> ~/brain
   cd ~/brain && ./bootstrap.sh
   ```
3. Personalize `people/me.md`.
4. Open a new Claude Code session anywhere and try `/remember` and `/recall`.

See `AGENTS.md` for the full read/write contract, conventions, never-store rule,
and how to use the vault from other harnesses.

## Variant: knowledge map inside a project repo

The same pattern, scoped to one system (a Salesforce org, an infra stack, a
warehouse): entity pages + index living in that repo's `docs/`, entered via the
repo's CLAUDE.md instead of skills, holding regenerable *structure* while
judgment/intent stays in your brain. See `docs/knowledge-map-variant.md` —
including the storage-split razor that decides where each fact lives.
