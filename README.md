# ambient-brain (template)

A portable, git-backed, **pure-markdown** memory vault for AI agents — a blank
"second brain" you can use with Claude Code (or any agent that reads files).
Organized Karpathy-style by entity (`people/ projects/ topics/ meetings/`) over
an immutable `sources/` bucket, plus a mutable `tasks.md` working set, with
three skills — `/remember`, `/recall`, `/lint` — and a one-command bootstrap.
No runtime, no database, no API key.

Battle-tested refinements baked in: incremental `/lint` (deep-checks only pages
changed since the last lint commit), the tasks log-vs-state split (meeting notes
are the immutable log; `tasks.md` is current state, done = delete the line),
commits that stage an explicit pathspec instead of `git add -A` so one session
cannot sweep another session's in-flight work into its commit, and a
global-rules block managed in-repo and installed by `bootstrap.sh`.

## `tasks.md` sorts by horizon, not by type

A list sorted by capture date buries the thing due tomorrow under whatever you
wrote down most recently. So the file has five sections, in order:

- **`## Now`** — a real deadline within ~2 weeks, or another named person is
  blocked waiting on it. **Hard cap: 7 items.** The only section read in a
  normal daily pass.
- **`## Next`** — actionable, no date pressure. The default landing spot.
- **`## Blocked`** — a named person or vendor owes you something; every line
  carries `(waiting on <name>)`.
- **`## Later`** — no urgency, not read in a normal pass.
- **`## Personal`** — life outside work; domain beats horizon.

The cap is the point. When an eighth item qualifies for `## Now`, something has
to be demoted or deleted. There is also a **21-day expiry rule**: `/lint` flags
undated items in `## Next` and `## Later` older than 21 days, so each one must
be dated, demoted, or deleted. `/lint` proposes and you decide — it never
deletes a task on its own.

## Optional: meeting auto-ingest

`install/fathom-autoingest/` adds a **macOS + Fathom specific** subsystem that
pulls meeting recordings into the vault twice a day via a LaunchAgent. It
commits raw transcripts to `main`, distils them into notes and task lines on a
rolling `fathom-ingest` branch, opens a draft PR, and surfaces what is waiting
at the start of your next session. Everything else in the template works
without it. It is **off by default**: install it with `./bootstrap.sh --with-fathom`.

## Set up with Claude Code (the easy way)

Give Claude Code this repo's URL and say "set this up". Instructions for the agent:

1. Ask the user for a name for their private vault repo (default `brain`) and
   confirm `~/brain` does not exist yet (if it does, stop and ask).
2. Create a **private** copy from this template and clone it:
   ```bash
   gh repo create <name> --private --template bhangalj/ambient-brain
   gh repo clone <name> ~/brain
   ```
   If `gh` is not logged in, ask the user to run `! gh auth login` first.
   If the clone fails straight after creation, wait a few seconds and retry.
3. Run `cd ~/brain && ./bootstrap.sh` (no flags — Fathom ingest stays off).
4. Ask the user for their name, role and team, fill in `people/me.md`, then
   commit and push that one file.
5. Tell the user to open a **new** Claude Code session and try `/remember` and `/recall`.

## Use this template (by hand)

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
