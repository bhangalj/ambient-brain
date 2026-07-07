<!-- BEGIN ambient-brain -->
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
