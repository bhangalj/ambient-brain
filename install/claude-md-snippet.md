<!-- BEGIN ambient-brain -->
# Global Rules (portable — managed in the brain repo, installed by bootstrap.sh)

<!-- CUSTOMIZE: the rules below are a working starting set — edit them to match
     how you work. The pattern that matters: your global agent rules live in
     THIS repo (version-controlled, portable across machines) and bootstrap.sh
     installs them into ~/.claude/CLAUDE.md alongside the brain block below. -->

## Scope
- Before making changes, confirm the exact scope of the request. Don't interpret
  requests more broadly than stated. Ask clarifying questions rather than assuming.
- Do not run `git init` or make git commits unless explicitly asked. Do not rename
  folders or directories without confirming downstream implications first.

## Hard safety rails (always in force — full detail in the vault topic pages)
<!-- CUSTOMIZE: one line per dangerous tool, each pointing at a topics/cli-<tool>.md
     page in the vault. Examples of the shape: -->
- **<messaging tool>: READ + DRAFT ONLY.** Never send/edit/delete — even if asked
  in the moment. Draft it; I send it. Detail: `__VAULT_DIR__/topics/cli-<tool>.md`
- **<CRM / database tool>:** verify the target environment/org explicitly before
  impactful commands; preview + state record counts before bulk writes.
  Detail: `__VAULT_DIR__/topics/cli-<tool>.md`

## CLI reference pages (read before non-trivial use)
Keep one `topics/cli-<tool>.md` page per CLI you use (command grammar, auth
identity, gotchas) and read it before using that tool for anything beyond a
trivial read.

# Ambient Brain (portable memory)

My durable, portable memory lives at `__VAULT_DIR__` — a git-backed markdown
vault. Its `AGENTS.md` defines how to read and write it. Current map of contents:

@__VAULT_DIR__/index.md

**Precedence:** For durable, cross-session, or personal facts (preferences,
people, project state, reference knowledge) this vault is the source of truth —
capture with `/remember`, look up with `/recall`. The native per-project memory
(`~/.claude/projects/*/memory/`) is only for disposable, project-local progress
notes; do not put durable/portable facts there.

**Ambient recall:** When a task depends on something you might have stored — a
person, project, past decision, or preference — consult the index above and read
the relevant entity page before answering. Treat it as memory you already have,
not a database you must be told to open.

**Never store** secrets, credentials, API keys, or regulated PII in the vault
(see the never-store rule in `AGENTS.md`).
<!-- END ambient-brain -->
