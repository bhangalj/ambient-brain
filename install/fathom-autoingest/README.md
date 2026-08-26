# Fathom auto-ingest

Ingests new Fathom recordings into the vault without anyone remembering to run
`/remember`. Installed by `bootstrap.sh`; runs twice daily (09:30 and 17:00 local) via a macOS
LaunchAgent, so it only ever runs while the laptop is on and catches up on wake
rather than skipping a missed slot.

## The shape

```
launchd (09:30 + 17:00 local)
  └─ run.sh
       ├─ preflight: clean tree? on main? git auth ok?      ── else defer
       ├─ fetch_transcripts.py                              ── 0 new? exit, no LLM
       ├─ commit raw transcripts ─────────────────────────────► main
       ├─ claude -p  (distil: notes, project Logs, tasks.md)
       └─ commit + push ──────────────────────────────────────► branch fathom-ingest
                                                                 └─ draft PR
you
  └─ every Claude Code session: pending.sh prints what is waiting
       └─ gh pr ready <branch>; gh pr merge <branch> --squash --delete-branch
                                    (`ready` first — the PR is opened as a draft)
```

## Why it is built this way

**Raw transcripts go to `main`, distillation goes to a branch.** The fetcher's
delta anchor is "newest day-folder on disk", so raw files stranded on an
unmerged branch would be re-fetched every run forever. Raw sources are also
immutable fact carrying no judgment, so there is nothing to review. The
*distillation* is the part with judgment in it, and that is what waits for you.

**One rolling branch, not one per day.** Because raw sources land on `main`, a
second dated branch cut from `main` would carry its own edits to `tasks.md`,
`meetings/_index.md` and the same project pages as the first. One accumulating
branch means one PR and no conflicts, however long it goes unreviewed.

**A spent rolling branch is recut, not reused.** A squash-merge lands the
branch's work on `main` under a new commit id, and the same content also reaches
`main` by other routes — a `/remember` session edits these very pages all week.
Either way the ref can survive with nothing left to give. So before reusing it,
`run.sh` asks what lines the branch would *add* to `main`; none means it is
spent, and it is deleted locally and on the remote and cut again from `main`.
The check is by content, never by commit count: `rev-list --count main..branch`
stays non-zero for ever here, because `run.sh` merges `main` back into the
branch on every run.

**The model never touches git.** `claude -p` is invoked with a file-tools-only
allowlist and no Bash, so it cannot push, merge, or reach the network. Every git
operation lives in `run.sh` where it can be read.

**The cost gate is the zero-new check.** A quiet run never invokes the model.

**Distillation is billed to a Console key, not the subscription.** `run.sh`
reads an Anthropic Console API key from the macOS login keychain before invoking
`claude -p`. An unattended run once died on "You've hit your monthly spend
limit" — an interactive limit with nothing to do with this job — and took that
day's meeting notes with it. Console spend is metered separately, so the
unattended job no longer competes with the sessions you are sitting in front of.

You create the keychain item yourself, once; no key is stored in this repo:

```bash
security add-generic-password -a "$USER" -s ANTHROPIC_API_KEY -w
# paste your Console key at the prompt
```

The lookup is by service name only, so you can delete and re-create the item
without editing the script. Override the service name with
`FATHOM_INGEST_KEY_SERVICE=<name>`. If the item is missing the run logs a
warning and falls back to whatever auth `claude` finds.

**`pending.sh` reports failures as well as work.** A cron that dies silently
looks exactly like a cron with nothing to do, and that second failure is the
expensive one — so the hook also flags a failed last run, a job that has not
fired in 3 days, and a job installed but never run.

## When a run goes wrong

Every failure mode here has the same shape: the job must not wedge itself, and
it must not go quiet.

- **It always ends on `main` with a clean tree.** The preflight defers when HEAD
  is elsewhere or the tree is dirty, so any exit path that left the vault on the
  ingest branch would stop every later run for ever. One `trap` owns that,
  including on SIGTERM at logout. Anything uncommitted at that point is
  `git stash`ed, never discarded — `git stash list` gets it back.
- **A half-finished distillation is committed, not thrown away.** If `claude -p`
  dies mid-edit, what it wrote is committed to the branch as `PARTIAL` and the
  run is recorded as an error. You see both.
- **Raw transcripts are committed even when the fetch fails**, because the
  fetcher is not transactional and files it left behind would otherwise dirty
  the tree for ever.
- **Repeated deferrals stop refreshing the status file**, so `pending.sh`'s
  3-day staleness check still fires on a job that runs twice a day and defers
  every time — which is just as broken as one that never runs.
- **A branch whose work is already on `main` cannot wedge the job.** It used to:
  `main` keeps editing the same pages, so merging `main` into a spent branch
  eventually conflicted and the run stopped on "resolve by hand" — a silent stop,
  the exact failure this automation exists to prevent. One such branch reached 87
  commits with zero exclusive files and zero added lines, holding an empty PR
  open and nagging at every session start. Spent branches are now detected by
  content and recut before the merge can happen.

## Files

| File | Role |
|---|---|
| `run.sh` | the pipeline; safe to run by hand at any time |
| `pending.sh` | SessionStart hook — prints pending work, silent when there is none |
| `com.ambient-brain.fathom-autoingest.plist` | the schedule; `__VAULT_DIR__` + `__HOME__` interpolated at install |

State lives in `.git/fathom-autoingest.{status,pr}` (untracked by definition).
Logs are at `~/Library/Logs/fathom-autoingest.{log,out,err}`.

## Operating it

```bash
bash install/fathom-autoingest/run.sh          # run now (respects the lock)
ANTHROPIC_API_KEY=... bash install/fathom-autoingest/run.sh   # override the key
bash install/fathom-autoingest/pending.sh      # what is waiting?
launchctl list | grep fathom                   # is it loaded?
launchctl kickstart -k gui/$(id -u)/com.ambient-brain.fathom-autoingest   # force a run
tail -f ~/Library/Logs/fathom-autoingest.log
FATHOM_INGEST_MODEL=opus bash install/fathom-autoingest/run.sh   # richer one-off
```

To change the schedule, edit the plist **here** and re-run `bootstrap.sh` — the
copy in `~/Library/LaunchAgents/` is overwritten on every bootstrap.

To pause it: `launchctl bootout gui/$(id -u)/com.ambient-brain.fathom-autoingest`.

## What it will not do

It never merges its own PR, never sends anything outward, and defers entirely
if the working tree is dirty or you are on another branch — it will not fight a
session you are in the middle of.
