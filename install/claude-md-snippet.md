<!-- BEGIN ambient-brain -->
# Global Rules (portable — managed in the brain repo, installed by bootstrap.sh)

<!-- CUSTOMIZE: the rules below are a working starting set — edit them to match
     how you work. The pattern that matters: your global agent rules live in
     THIS repo (version-controlled, portable across machines) and bootstrap.sh
     installs them into ~/.claude/CLAUDE.md alongside the brain block below.
     Throughout this block, "I" and "my" mean you, the vault owner, and "you"
     means the agent reading the file. -->

## Global communication style (applies to every reply)
<!-- CUSTOMIZE: state how you want the agent to talk to you. The example below is
     one working set; swap in your own reading preferences. -->
- Write short sentences. Use active voice. Give one instruction per sentence.
  Do not use idioms or unnecessary jargon.
- Start with the answer. Use short sections. Use clear bullets. Give the next
  action clearly.

## Drafting in MY voice (different from the rule above)
<!-- CUSTOMIZE: this only pays off once you have a measured style page in the
     vault. Write `topics/my-communication-style.md` from a real sample of your
     own sent messages, then point this rule at it. -->
- The rule above governs **your replies to me**. **Anything that goes out UNDER MY NAME**
  — email, chat messages, DMs, PR descriptions, doc prose, review comments — is a
  different job: **read `__VAULT_DIR__/topics/my-communication-style.md` BEFORE writing
  a word.** It is measured from my own past messages and it is the source of truth.
  Do not draft from memory of it and do not summarise it here — read it.
- **If I edit your draft before sending, that is data.** Say what changed and offer to add it
  to that page with `/remember`.

## Scope
- Before making changes, confirm the exact scope of the request. Don't interpret
  requests more broadly than stated. Ask clarifying questions rather than assuming.
- Do not run `git init` or make git commits unless explicitly asked. Do not rename
  folders or directories without confirming downstream implications first.
- **Surface adjacent long-term wins.** If while working on a narrow task you spot
  already-documented dedup opportunities, "planned later" work the current change
  naturally unlocks, or duplication a clean fix would collapse — **surface them with
  narrow-vs-expanded tradeoffs so I can pick**. Don't silently expand scope; also
  don't ignore cleanly aligned wins and leave the codebase with more call paths than
  it started with. The user decides, not you.

## Default workflow for code work
- For any code-writing task (new feature, bug fix, refactor), default to test-driven
  development — write the failing test first, confirm it fails, then write the minimum
  code to pass. Skip this only for trivial edits (typo fixes, one-line config tweaks,
  docs) or when I explicitly say "no tests" / "quick hack".
- Prefer the simplest solution that works. Three lines inline at two callsites beats a
  20-line helper used once. Abstraction is earned by a third callsite, not designed for
  it. If a fix wants a new module/helper/registry/constant used from exactly one place,
  inline it instead.
- For any implementation that spans more than ~30 LOC or touches more than 2 files,
  pause and confirm the approach with me before writing code — even if the earlier
  conversation implied agreement. One-sentence restatement of what's about to happen
  is enough.
- When fixing bugs, verify the fix doesn't introduce new bugs in related components.
  Check adjacent code paths that share state or logic with what you changed.

## Verification
- After implementing fixes, always run the full test suite and report the result
  clearly. Format: "All X/X tests passing." If there is no test suite, say so.

## Hard safety rails (always in force — full detail in the vault topic pages)
<!-- CUSTOMIZE: one line per dangerous tool, each pointing at a topics/cli-<tool>.md
     page in the vault. Examples of the shape: -->
- **<messaging tool>: READ + DRAFT ONLY.** Never send/edit/delete/react/mark-read/upload
  — even if asked in the moment. Draft it; I send it.
  Detail: `__VAULT_DIR__/topics/cli-<tool>.md`
- **<email tool>: READ + DRAFT ONLY.** Never send/delete/modify/label.
  Detail: `__VAULT_DIR__/topics/cli-<tool>.md`
- **<CRM / database tool>:** verify the target environment/org explicitly before
  impactful commands; preview + state record counts before bulk writes.
  Detail: `__VAULT_DIR__/topics/cli-<tool>.md`
- **<tool that spends money or credits>:** writes mutate live data and enrichment
  spends credits — confirm first. Detail: `__VAULT_DIR__/topics/cli-<tool>.md`

## CLI reference pages (read before non-trivial use)
Keep one `topics/cli-<tool>.md` page per CLI you use (command grammar, auth
identity, gotchas) — see the Topics section of the index below — and read the
matching page before using that tool for anything beyond a trivial read. Add a
cost-discipline page for any tool billed per query.

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
