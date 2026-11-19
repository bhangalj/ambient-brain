# ambient-brain

A memory vault for AI agents, kept as plain markdown in a git repo. Your agent
reads a short index at the start of every session, so it knows who you work
with, what your projects are and what you decided last month. You tell it to
remember things, and it files them as linked pages. There is no runtime, no
database and no API key. Any agent that reads files can use it. Claude Code
gets three skills and a one-command setup.

## The three verbs

- **`/remember`**: save something. A fact, a file, a URL or a meeting
  transcript. The raw copy goes to `sources/`, and the agent distils it into
  the right page, updates the index and commits.
- **`/recall`**: look something up. Read-only, with file citations.
- **`/lint`**: health-check the vault. It finds contradictions, stale claims,
  orphan pages, missing links, undistilled sources and leaked secrets. It
  proposes fixes and commits only when you say yes.

## Layout

| Path | Holds |
|---|---|
| `index.md` | one line per page; loaded into every session, so it stays short |
| `tasks.md` | your open tasks, sorted by horizon (Now, Next, Blocked, Later, Personal) |
| `people/` `projects/` `topics/` `meetings/` | one page per entity |
| `sources/` | raw, immutable material the pages were distilled from |
| `install/` | the skills and the global `CLAUDE.md` snippet |
| `bootstrap.sh` | setup: links the skills, adds the snippet, pins git auth |
| `AGENTS.md` | the full read/write contract and conventions |

[`AGENTS.md`](AGENTS.md) is the agent entry point. Read it for the conventions,
page schemas and task rules.

## Set up with your agent (the easy way)

Give your agent (Claude Code, Codex, Cursor, ...) this repo's URL and say "set this up". Instructions for the agent:

1. Create the user's own copy. Run `gh repo create <name> --template <owner>/ambient-brain --private --clone`, then move or clone the new repo to `~/brain` (or click **Use this template** on GitHub). For a local-only vault, clone this repo to `~/brain`, delete `.git`, run `git init` and skip the remote.
2. Run `./bootstrap.sh` from the vault root. It takes no flags. It links each skill in `install/skills/` into `~/.claude/skills/`, adds the vault block to `~/.claude/CLAUDE.md`, and on a GitHub HTTPS remote pins git auth to the repo owner. It is safe to run again.
3. Ask the user a few questions (name, role, team, what they work on) and fill in `people/me.md`.
4. Run a recall ("what do I know about me?") to confirm the brain is ambient. It must read `index.md` and `people/me.md`.

The skill links and the `CLAUDE.md` block in step 2 are Claude Code only. Another agent reads `AGENTS.md` and `index.md` at the start of each session instead.

## Quick start (by hand)

1. Click **Use this template** and create a **private** repo (for example
   `brain`). Local-only vault with no remote: clone this repo to `~/brain`,
   delete `.git`, run `git init`, and skip the clone in step 2.
2. Clone your repo and run the bootstrap:
   ```bash
   git clone <your-instance-repo-url> ~/brain
   cd ~/brain && ./bootstrap.sh
   ```
   This links the skills into `~/.claude/skills/`, adds the vault block to
   `~/.claude/CLAUDE.md`, and, on a GitHub HTTPS remote, pins the vault's git
   auth to the repo owner. It is safe to run again.
3. Fill in `people/me.md` with your name, role and team.
4. Open a new Claude Code session and try `/remember` and `/recall`.

## Other harnesses

- **Any agent (Codex, Cursor and others):** point it at the repo and say "read
  `AGENTS.md` and `index.md`, then recall X".
- **Claude.ai web or mobile:** add the GitHub connector and ask the same. This
  is read-only. Draft in chat and commit later from Claude Code.

## Never store

Git history is permanent. Keep secrets, credentials, API keys, tokens, `.env`
contents and regulated PII out of the vault. `/remember` redacts known secret
patterns before it writes, and `/lint` scans for leaks. The pattern list is in
`AGENTS.md` under "Never store".

## Variant: a knowledge map inside a project repo

The same pattern works for one system, such as a CRM org or a data warehouse.
See [`docs/knowledge-map-variant.md`](docs/knowledge-map-variant.md).
