# ambient-brain (template)

A portable, git-backed, **pure-markdown** memory vault for AI agents — a blank
"second brain" you can use with Claude Code (or any agent that reads files).
Organized Karpathy-style by entity (`people/ projects/ topics/ meetings/`) over
an immutable `sources/` bucket, with three skills — `/remember`, `/recall`,
`/lint` — and a one-command bootstrap. No runtime, no database, no API key.

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
