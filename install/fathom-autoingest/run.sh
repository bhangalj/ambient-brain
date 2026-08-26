#!/usr/bin/env bash
#
# Fathom auto-ingest — the unattended half of `/remember`'s Fathom playbook.
#
# Run twice daily by launchd (09:30 and 17:00 local) so new recordings are
# distilled without anyone remembering to ask. Two stages, deliberately split:
#
#   1. FETCH   deterministic, no LLM. fetch_transcripts.py pulls new transcripts
#              and they are committed straight to main. Raw sources are
#              immutable fact, carry no judgment, and — critically — the
#              script's delta anchor is "newest day folder ON DISK", so if the
#              raw files lived only on an unmerged branch every later run would
#              re-fetch them. They must land on main.
#
#   2. DISTIL  needs judgment, so it lands on a branch and waits for a human.
#              A headless `claude -p` writes the meeting notes / project Logs /
#              tasks.md edits, this script commits them to ONE rolling branch
#              and opens a draft PR.
#
# Why one rolling branch and not one per day: stage 1 puts raw sources on main,
# so a second dated branch cut from main would carry its own edits to tasks.md,
# meetings/_index.md and the same project pages as the first — guaranteed
# conflicts at merge time. One accumulating branch means one PR and no
# conflicts, however many days go unreviewed.
#
# The LLM never touches git: it is invoked with a file-tools-only allowlist and
# no Bash at all, so it cannot push, merge, or reach the network. Every git
# operation here is in this script, where it can be read.
#
# Exit code is 0 for "nothing to do" as well as success — launchd treats a
# non-zero exit as a job failure and this job idles most of the time.

set -uo pipefail

# launchd hands over a near-empty PATH; python3/gh/claude all live outside it.
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

VAULT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
INGEST_BRANCH="fathom-ingest"
FETCHER="$VAULT/sources/fathom-transcripts/fetch_transcripts.py"
PLAYBOOK="install/skills/remember/references/fathom-ingest.md"

# State lives in .git/ — untracked by definition, so it never pollutes a diff.
STATUS_FILE="$VAULT/.git/fathom-autoingest.status"
PR_FILE="$VAULT/.git/fathom-autoingest.pr"

LOG_DIR="$HOME/Library/Logs"
LOG="$LOG_DIR/fathom-autoingest.log"
LOCK="${TMPDIR:-/tmp}/fathom-autoingest.lock"

# Distillation is bounded-scope reasoning, so Sonnet is the default tier.
# Override with FATHOM_INGEST_MODEL=opus for a one-off richer pass.
MODEL="${FATHOM_INGEST_MODEL:-sonnet}"

# Batch cap for a single distillation run; the remainder is picked up next run.
MAX_PER_RUN="${FATHOM_INGEST_MAX:-8}"

# Keychain service holding the Anthropic Console API key used for distillation.
# You create this item yourself — see the README, "Distillation is billed to a
# Console key". Nothing here ships with a key in it.
API_KEY_SERVICE="${FATHOM_INGEST_KEY_SERVICE:-ANTHROPIC_API_KEY}"

mkdir -p "$LOG_DIR"
log() { printf '%s  %s\n' "$(date -u +%FT%TZ)" "$*" >>"$LOG"; }

# `gh` serves the ACTIVE account's token, which on a multi-account machine is
# often not the vault owner — `gh pr create` then fails with "Could not resolve
# to a Repository". bootstrap.sh already solves this for git via a repo-local
# credential helper; mirror it for gh by resolving the owner from the remote and
# passing their token per-invocation. Never `gh auth switch`: it flips global
# state and races parallel sessions (AGENTS.md, "Git auth on multi-account
# machines").
# -n/p so a non-GitHub remote yields an EMPTY owner rather than the whole URL,
# which would otherwise be handed to `gh auth token --user`.
GH_OWNER="$(git -C "$VAULT" remote get-url origin 2>/dev/null \
  | sed -nE 's#.*github\.com[:/]([^/]+)/.*#\1#p')"
gh_() {
  local tok
  tok="$(command gh auth token --user "$GH_OWNER" 2>/dev/null)"
  if [ -n "$tok" ]; then
    GH_TOKEN="$tok" command gh "$@"
  else
    command gh "$@"
  fi
}

# Record why a run stopped so the SessionStart hook can surface a broken cron.
# A silently dead automation is the failure mode this whole thing exists to
# avoid, so "it errored" has to be as visible as "it produced work".
#
# One subtlety: pending.sh uses this file's MTIME as the liveness signal, so a
# repeated `skipped` must NOT refresh it. A job that defers every run for a
# fortnight (an untracked stray file, a branch left checked out) is as broken as
# one that never fires, and refreshing the mtime would hide exactly that.
finish() {
  if [ "$1" = skipped ] && [ "$(cut -f1 "$STATUS_FILE" 2>/dev/null)" = skipped ]; then
    log "$1 ${2:-} (still deferring; status file left at its first deferral)"
    exit "${3:-0}"
  fi
  printf '%s\t%s\t%s\n' "$1" "$(date -u +%FT%TZ)" "${2:-}" >"$STATUS_FILE"
  log "$1 ${2:-}"
  exit "${3:-0}"
}

# Deliberately NOT a macOS notification. A banner fires whether or not you are
# at the machine, is gone a few seconds later, and is unactionable at the moment
# it appears. The status file + log are the record, and `pending.sh` surfaces
# them IN Claude Code at session start, where you are already in a position to
# act. Keeping the call sites means the message still reaches the log; only the
# banner is gone.
#
# Trade-off accepted: a failure at 14:00 is now seen at the next session start
# rather than immediately. `pending.sh`'s staleness check (STALE_DAYS) is the
# backstop for the job dying silently.
notify() {
  log "note: $1"
}

# ---------------------------------------------------------------- lock -------
# mkdir is atomic on macOS (no flock binary). The holder's pid goes inside it so
# a run killed mid-flight (logout, shutdown, kill) frees the lock on the very
# next attempt instead of blocking for hours, while a genuinely long run keeps it
# however long it takes — a time-only heuristic gets both of those backwards.
# The mmin fallback only covers the sliver between mkdir and the pid write.
if ! mkdir "$LOCK" 2>/dev/null; then
  LOCK_PID="$(cat "$LOCK/pid" 2>/dev/null || true)"
  if { [ -n "$LOCK_PID" ] && kill -0 "$LOCK_PID" 2>/dev/null; } ||
     { [ -z "$LOCK_PID" ] && [ -z "$(find "$LOCK" -maxdepth 0 -mmin +120 2>/dev/null)" ]; }; then
    log "another run in progress (pid ${LOCK_PID:-unknown}) — skipping"
    exit 0
  fi
  log "clearing stale lock (holder ${LOCK_PID:-unknown} is gone)"
  rm -rf "$LOCK"
  mkdir "$LOCK" 2>/dev/null || { log "could not take lock"; exit 0; }
fi
printf '%s\n' "$$" >"$LOCK/pid"

# The one place that guarantees the invariant every other run depends on: this
# script always leaves the vault clean and on `main`. The preflight defers when
# HEAD is elsewhere or the tree is dirty, so a single exit path that forgot to
# switch back would wedge the job for ever.
#
# Leftovers are stashed rather than reset: carrying them to main would poison
# every future preflight, and discarding them could eat a note a human happened
# to write while the run was in flight. `git stash list` gets them back.
ON_INGEST_BRANCH=0
cleanup() {
  if [ "$ON_INGEST_BRANCH" -eq 1 ]; then
    if [ -n "$(git -C "$VAULT" status --porcelain)" ]; then
      if git -C "$VAULT" stash push -u -q -m "fathom-autoingest leftovers $(date -u +%FT%TZ)" 2>/dev/null; then
        log "WARNING: uncommitted leftovers stashed before returning to main (git stash list)"
      else
        log "WARNING: could not stash uncommitted leftovers"
      fi
    fi
    git -C "$VAULT" checkout -q main 2>/dev/null ||
      log "WARNING: could not return to main — vault left on $INGEST_BRANCH"
  fi
  rm -rf "$LOCK"
}
trap cleanup EXIT
# An untrapped signal skips the EXIT trap; launchd sends SIGTERM at logout.
trap 'exit 143' HUP INT TERM

cd "$VAULT" || { log "vault not found at $VAULT"; exit 1; }

# ------------------------------------------------------- safety preflight ----
# Never fight a human. A dirty tree or a checked-out feature branch means
# someone is mid-edit; the run defers to the next slot rather than stashing or
# switching branches under them.
if [ -n "$(git status --porcelain)" ]; then
  finish skipped "working tree dirty — deferring to next run"
fi

CURRENT="$(git rev-parse --abbrev-ref HEAD)"
if [ "$CURRENT" != "main" ]; then
  finish skipped "on branch '$CURRENT', not main — deferring to next run"
fi

if ! git ls-remote -q origin HEAD >/dev/null 2>&1; then
  notify "Git auth failed — run bootstrap.sh"
  finish error "git auth preflight failed — run: bash $VAULT/bootstrap.sh" 1
fi

# A failed rebase leaves conflicts in the tree and HEAD detached, which the next
# run's preflight reads as "a human is mid-edit" — deferring for ever. Abort so
# the failure is a single bad run, not a wedged job.
git pull --rebase -q || {
  git rebase --abort 2>/dev/null
  finish error "git pull --rebase failed (rebase aborted; vault left on main)" 1
}

# ------------------------------------------------------------- 1. fetch ------
# A plain assignment does not swallow the exit status the way `local x=$(...)`
# would, so this really is the fetcher's status.
FETCH_OUT="$(python3 "$FETCHER" 2>&1)"
FETCH_RC=$?

# The fetcher prints each newly written file as "  + <date>/<file>.md".
NEW_FILES="$(printf '%s\n' "$FETCH_OUT" | sed -n 's/^  + //p')"
NEW_COUNT="$(printf '%s' "$NEW_FILES" | grep -c . )"

# Commit whatever landed on disk BEFORE branching on the result. The fetcher is
# not transactional — it can die having written half a day, and it rewrites
# INDEX.md on every run — and anything it leaves uncommitted reads to the next
# preflight as "a human is mid-edit", deferring the job for ever.
if [ -n "$(git status --porcelain -- sources/fathom-transcripts)" ]; then
  if [ "$NEW_COUNT" -gt 0 ]; then
    RAW_MSG="sources: $NEW_COUNT new Fathom transcript(s)"
  else
    RAW_MSG="sources: refresh Fathom transcript index"
  fi
  git add sources/fathom-transcripts
  git commit -q -m "$RAW_MSG" || finish error "commit of raw transcripts failed" 1
  git push -q || finish error "push of raw transcripts to main failed" 1
fi

if [ "$FETCH_RC" -ne 0 ]; then
  log "$FETCH_OUT"
  notify "Transcript fetch failed — see log"
  finish error "fetch_transcripts.py exited $FETCH_RC" 1
fi

[ "$NEW_COUNT" -gt 0 ] && log "fetched $NEW_COUNT new transcript(s)"

# Which transcripts still have no meeting note?
#
# The fetcher's "new" list is the WRONG signal for this. It reports what it just
# WROTE, so a transcript already on disk from a run whose distillation failed —
# or one fetched by a human running the script by hand — is invisible for ever:
# the next fetch reports 0 new and the run exits at the cost gate. The playbook
# says it outright ("Transcripts on disk are not necessarily distilled:
# cross-check both lists, don't assume"), so derive the work from disk-vs-notes
# and treat the fetch as nothing more than topping up disk. That makes the job
# self-healing: anything missed is simply picked up on the next run.
#
# "Distilled" = some meeting note cites the transcript in its `source:` link.
# Deliberate skips are recorded in SKIPPED.md, otherwise a meeting judged not
# worth a note would be re-analysed by the model on every single run, for ever.
undistilled() {
  python3 - "$VAULT" <<'PY'
import pathlib, re, sys

vault = pathlib.Path(sys.argv[1])
src = vault / "sources" / "fathom-transcripts"

def stem(cited):
    """Normalise a cited or skipped transcript to the key matched against disk.

    Entries reach here in three spellings that all name the same file:
    `<date>/<name>.md` (the SKIPPED.md format below, and how notes cite),
    `<name>.md`, and a bare `<name>`. Only the stem is ever compared, so a
    mismatch here does not error — it silently records a skip that suppresses
    nothing and re-analyses the meeting on every run, for ever.
    """
    return cited.rsplit("/", 1)[-1].removesuffix(".md")

done = set()
for note in (vault / "meetings").glob("*.md"):
    try:
        text = note.read_text(errors="replace")
    except OSError:
        continue
    for m in re.finditer(r"fathom-transcripts/[^/\s]+/([^\]\s\"']+)", text):
        done.add(stem(m.group(1)))

skipped = src / "SKIPPED.md"
if skipped.exists():
    # LIST ENTRIES ONLY. Scanning every backtick in the file also swallows its
    # own prose -- it names `install/fathom-autoingest/run.sh` and `<name>` --
    # which puts junk stems like "run" in `done` and would silently suppress a
    # real transcript that happened to share the name.
    for line in skipped.read_text(errors="replace").splitlines():
        if not line.lstrip().startswith("- "):
            continue
        m = re.search(r"`([^`]+)`", line)
        if m:
            done.add(stem(m.group(1)))

for day in sorted(d for d in src.glob("[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]") if d.is_dir()):
    for f in sorted(day.glob("*.md")):
        if f.stem not in done:
            print(f"{day.name}/{f.name}")
PY
}

# Checked against main's notes first, so a quiet run costs neither a branch
# checkout nor a token. Recomputed after checkout, because notes distilled onto
# the pending branch are not visible from main.
if [ -z "$(undistilled)" ]; then
  finish ok "nothing undistilled"
fi

# ---------------------------------------------------- 2. branch + distil -----
# From here to the end of the run, `cleanup` owns getting back to main.
REUSED_BRANCH=0
RECREATED_BRANCH=0
if git show-ref --verify --quiet "refs/heads/$INGEST_BRANCH"; then
  git checkout -q "$INGEST_BRANCH" || finish error "could not check out $INGEST_BRANCH" 1
  ON_INGEST_BRANCH=1
  REUSED_BRANCH=1
elif git ls-remote --exit-code --heads origin "$INGEST_BRANCH" >/dev/null 2>&1; then
  git checkout -q -b "$INGEST_BRANCH" "origin/$INGEST_BRANCH" || finish error "could not track origin/$INGEST_BRANCH" 1
  ON_INGEST_BRANCH=1
  REUSED_BRANCH=1
else
  git checkout -q -b "$INGEST_BRANCH" main || finish error "could not create $INGEST_BRANCH" 1
  ON_INGEST_BRANCH=1
fi

# Is the ref we just picked up still carrying anything? A squash-merge puts this
# branch's work on main under a NEW commit id and normally deletes the branch,
# but the ref survives whenever the merge happened somewhere this checkout cannot
# see — the web UI, another clone, `gh pr merge` run from outside the vault — and
# it survives too when the same content reaches main by another route entirely,
# which is what a `/remember` session does to these pages all week.
#
# Reusing a spent branch does real damage, not just noise. Its content is already
# on main, so the PR it holds open has an empty diff, and pending.sh nags every
# session about work reviewed days ago. Worse, main keeps editing the same pages,
# so the `git merge main` below eventually CONFLICTS and the job stops ingesting
# altogether on "resolve by hand" — a silent stop, which is the exact failure this
# whole automation exists to prevent. Seen in practice: a branch at 87 commits
# with zero exclusive files and zero added lines, one main-side edit away from
# wedging.
#
# So test BEFORE merging, and by content: what lines would this branch add to
# main? None means it is spent. Recreate rather than reset, so the stale remote
# ref goes with it — deleting that ref also closes its empty PR, so the push at
# the end of this run opens a clean one instead of reviving the old.
if [ "$REUSED_BRANCH" -eq 1 ]; then
  if [ "$(git diff "main..$INGEST_BRANCH" | grep -c '^+[^+]')" -eq 0 ]; then
    log "$INGEST_BRANCH adds nothing to main — discarding it and cutting a fresh one"
    git checkout -q main || finish error "could not return to main to recreate $INGEST_BRANCH" 1
    ON_INGEST_BRANCH=0
    git branch -q -D "$INGEST_BRANCH" || finish error "could not delete spent $INGEST_BRANCH" 1
    git push -q origin --delete "$INGEST_BRANCH" 2>/dev/null ||
      log "no stale origin/$INGEST_BRANCH to delete (or the delete was refused)"
    git checkout -q -b "$INGEST_BRANCH" main || finish error "could not recreate $INGEST_BRANCH" 1
    ON_INGEST_BRANCH=1
    RECREATED_BRANCH=1
    # The PR that file names is the empty one just closed; leave no pointer to it.
    rm -f "$PR_FILE"
  else
    git merge -q --no-edit main || {
      git merge --abort 2>/dev/null
      notify "Ingest branch conflicts with main — resolve by hand"
      finish error "merging main into $INGEST_BRANCH conflicted — resolve by hand" 1
    }
  fi
fi

# Recompute now that the branch's own notes are visible; a pending branch may
# already have distilled what main still thinks is outstanding.
TODO="$(undistilled)"
if [ -z "$TODO" ]; then
  finish ok "nothing undistilled (already covered on $INGEST_BRANCH)"
fi

# Cap the batch. Coming back from three weeks away should not hand the model
# forty transcripts in one context — the rest are picked up on the next run,
# since the work-list is derived from disk each run rather than from this fetch.
# Log what was deferred: a silent cap reads as "everything was covered".
TODO_TOTAL="$(printf '%s\n' "$TODO" | grep -c .)"
if [ "$TODO_TOTAL" -gt "$MAX_PER_RUN" ]; then
  log "$TODO_TOTAL undistilled; taking $MAX_PER_RUN this run, $((TODO_TOTAL - MAX_PER_RUN)) deferred to the next"
  TODO="$(printf '%s\n' "$TODO" | head -n "$MAX_PER_RUN")"
fi
TODO_COUNT="$(printf '%s\n' "$TODO" | grep -c .)"

PROMPT="You are running headless and unattended as the automated Fathom meeting ingest for this markdown brain vault. Nobody will answer a question, so make the best defensible call and record any doubt in your summary.

Follow the playbook at $PLAYBOOK, STEPS 2 THROUGH 7 ONLY.

Step 1 (fetch) and step 8 (commit/push) are already handled by the wrapper script that invoked you:
- The transcripts below are ALREADY fetched and committed. Do not run fetch_transcripts.py.
- Do NOT commit, push, or run any git command. You have no Bash tool. The wrapper commits your work to a branch and opens a pull request for human review.

Transcript files to distil, relative to sources/fathom-transcripts/:
$TODO

Hard requirements:
- Read AGENTS.md first and follow its conventions exactly.
- Every meeting note MUST carry a source: link of the form
  source: \"[[../sources/fathom-transcripts/<date>/<basename-without-.md>]]\"
  This link is not decoration: the wrapper decides what still needs distilling by
  checking which transcripts are cited by a note. A note without it means the
  same meeting is distilled again on the next run.
- tasks.md edits must follow AGENTS.md -> 'Tasks: sections', the horizon convention. The file holds exactly five headings in this order: ## Now, ## Next, ## Blocked, ## Later, ## Personal. Route each new line by horizon: personal-life items always go under ## Personal (flat, newest first); a named person or vendor owes something first -> ## Blocked, and that line MUST carry '(waiting on <name>)'; a real deadline within about two weeks, or another named person blocked waiting on it -> ## Now; actionable now with no date pressure -> ## Next; more than about a quarter out, or no urgency -> ## Later. ## Now has a HARD CAP of 7 lines - if it already holds 7, either demote a less urgent existing ## Now line to ## Next or put the new item in ## Next instead. Write every task line as '- **<task>** ... — [[meetings/YYYY-MM-DD-<slug>|src]] (YYYY-MM-DD)', where the trailing date is the capture date. Sort newest-capture first everywhere except ## Now, which sorts soonest-deadline first. Never leave a task line outside a heading.
- Verify every person slug against people/_index.md before wikilinking. Do not invent slugs.
- RESOLVE MANGLED PROPER NOUNS AGAINST THE VAULT, THEN GLOSS THEM. Fathom
  mis-transcribes the same names on every single call, and the vault already
  knows the answers: earlier meeting notes carry proper-noun caveat blocks (grep
  meetings/ for 'caveat'), people/_index.md holds every real name and slug, and
  topics/ pages fix product and vendor spellings. Before you write a name, check
  it against those. Cross-check the transcript's own Participants block too: a
  name spoken 17 times by someone who is not in the room is a mis-transcription,
  not a guest.
  Then WRITE A PROPER-NOUN CAVEAT BLOCK near the top of the note listing every
  resolution you made ('X' -> [[people/y|Y]]). This is not optional bookkeeping.
  A note that omitted this block let three names the previous day's note had
  already resolved regress silently - the wrong person got wikilinked in four
  pages and a task. The block is what stops the next run undoing the last one.
  If you genuinely cannot resolve a name, say so explicitly and mark it
  unconfirmed rather than inventing a slug or picking the closest-looking page.
- BACK-LINK EVERY ATTENDEE - AND ONLY ATTENDEES. For each meeting note you
  write, add it to the '## Meetings' list on the people/<slug>.md page of everyone
  who WAS ACTUALLY IN THE ROOM (skip people/me.md). The people: frontmatter is NOT
  that list - it also carries people merely discussed, so a 1:1 can name ten. Take
  attendance from the transcript's Participants block, falling back to its speaker
  labels when Fathom records only the host (huddle-style calls do this). A
  '## Meetings' entry asserts the person was there; a backfill that trusted
  people: instead once put 71 meetings on the pages of people who never attended
  them. If someone is only discussed, leave their page alone, or annotate the
  entry '(mentioned, not present)'. Newest first, matching that page's own line
  format, with a one-line hook - person-specific where the note attributes
  something to them, describing the meeting itself where it does not. If a person
  page has no '## Meetings' section, do not invent one; say so in your summary.
  These lists are how a person page answers 'when did I last speak to them', and
  they go unmaintained the moment nothing in this prompt asks for them.
- Own recordings only (playbook step 2). Skip anything not recorded by the vault owner.
- Never copy a secret or credential out of a transcript into a distilled note.
- If a meeting is NOT worth a note, you must record it in
  sources/fathom-transcripts/SKIPPED.md (create it if absent) as a line:
      - \`<date>/<filename.md>\` — <one-line reason> (<today's date>)
  Anything neither distilled nor listed there is retried on every run, for ever.

End your reply with a plain-text summary of 3 to 8 lines: which meetings you distilled, which pages you touched, and anything you were unsure about. That summary becomes the pull request body a human reads, so write it for them."

# Bill the distillation to an Anthropic Console API key held in the login
# keychain, not to the Claude subscription. An unattended run once died on
# "You've hit your monthly spend limit" — an interactive limit that has nothing
# to do with this job, yet it took that day's meeting notes down with it.
# Console spend is metered separately, so the unattended job no longer competes
# with the sessions you are actually sitting in front of.
#
# You create the keychain item yourself, once:
#   security add-generic-password -a "$USER" -s ANTHROPIC_API_KEY -w
# and paste the key at the prompt. No key is stored in this repo, ever.
#
# Lookup is by service only, so the item can be re-created without editing this
# script. A failure here degrades rather than wedges: an empty key is unset and
# `claude` falls back to whatever auth it finds, which is exactly the behaviour
# without the item. The warning is emitted here rather than at the top of the run
# so a quiet run — which never invokes the model — stays silent in the log.
if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
  KEY="$(security find-generic-password -s "$API_KEY_SERVICE" -w 2>/dev/null)"
  if [ -n "$KEY" ]; then
    export ANTHROPIC_API_KEY="$KEY"
  else
    log "WARNING: no '$API_KEY_SERVICE' in the login keychain — falling back to subscription auth"
  fi
  unset KEY
fi

# File tools only. No Bash means the model categorically cannot run git, reach
# the network, or execute anything — the blast radius is edits inside the vault,
# which is exactly what the branch-plus-review flow is designed to contain.
CLAUDE_OUT="$(claude -p "$PROMPT" \
  --model "$MODEL" \
  --permission-mode acceptEdits \
  --allowedTools Read Write Edit Glob Grep \
  --add-dir "$VAULT" 2>&1)"
CLAUDE_RC=$?

if [ "$CLAUDE_RC" -ne 0 ]; then
  log "$CLAUDE_OUT"
  # Park any half-written edits on the branch, where the PR shows them to a
  # human. Left in the tree they would only reach `cleanup`'s stash, and had we
  # simply switched branches they would have followed us onto main and made
  # every future preflight see a dirty tree.
  if [ -n "$(git status --porcelain)" ]; then
    git add -A
    git commit -q -m "ingest: PARTIAL distillation of $TODO_COUNT transcript(s) — claude -p exited $CLAUDE_RC" ||
      log "could not commit partial distillation; it will be discarded"
  fi
  notify "Distillation failed — transcripts are safe on main"
  finish error "claude -p exited $CLAUDE_RC (raw transcripts are committed on main)" 1
fi

log "distillation finished"

if [ -z "$(git status --porcelain)" ]; then
  notify "$TODO_COUNT transcript(s) reviewed; nothing worth distilling"
  finish ok "claude produced no vault changes for $TODO_COUNT transcript(s)"
fi

git add -A
git commit -q -m "ingest: distil $TODO_COUNT Fathom meeting(s)

$(printf '%s\n' "$TODO" | sed 's/^/- /')" || finish error "commit of distillation failed" 1

# A recreated branch has a new root, so if the delete above was refused the push
# is a non-fast-forward and would strand the distillation locally — and strand it
# again every run after, since the branch now carries content and takes the merge
# path. Forcing is safe here and only here: we proved by content that the ref we
# replaced added nothing to main. --force-with-lease still refuses if the remote
# moved to something our tracking ref has not seen.
if [ "$RECREATED_BRANCH" -eq 1 ]; then
  git push -q --force-with-lease -u origin "$INGEST_BRANCH" ||
    finish error "push of recreated $INGEST_BRANCH failed — work is committed locally" 1
else
  git push -q -u origin "$INGEST_BRANCH" ||
    finish error "push of $INGEST_BRANCH failed — work is committed locally" 1
fi

# ---------------------------------------------------------------- 3. PR ------
# `gh pr view <branch>` also matches a CLOSED or MERGED PR, and this branch is
# recreated after every squash-merge — so it would happily hand back last week's
# merged PR and we would never open one for the work just pushed. List open PRs
# for the head branch instead.
PR_URL="$(gh_ pr list --head "$INGEST_BRANCH" --state open --json url -q '.[0].url // empty' 2>/dev/null)"
if [ -z "$PR_URL" ]; then
  if PR_OUT="$(gh_ pr create --draft --base main --head "$INGEST_BRANCH" \
    --title "Fathom ingest — pending review" \
    --body "Automated Fathom ingest. Raw transcripts are already on \`main\`; this PR is the distillation only.

$CLAUDE_OUT

---
Generated by \`install/fathom-autoingest/run.sh\`. Review the diff, then:

\`\`\`
gh pr ready $INGEST_BRANCH; gh pr merge $INGEST_BRANCH --squash --delete-branch
\`\`\`

(\`pr ready\` first because this PR is opened as a draft, and \`gh pr merge\`
refuses a draft. On a multi-account machine prefix both with
\`GH_TOKEN=\"\$(gh auth token --user <vault-owner>)\"\`.)" 2>&1)"; then
    # stdout carries the URL, but stderr (folded in for the failure log) can
    # carry gh warnings too — pick the URL out rather than storing the lot.
    PR_URL="$(printf '%s\n' "$PR_OUT" | grep -Eom1 'https://[^[:space:]]+/pull/[0-9]+')"
  else
    log "gh pr create failed: $PR_OUT"
    PR_URL=""
  fi
fi

if [ -n "$PR_URL" ]; then
  printf '%s\n' "$PR_URL" >"$PR_FILE"
else
  log "could not create or find a PR; branch is pushed"
  rm -f "$PR_FILE"
fi

notify "$TODO_COUNT meeting(s) distilled — review the ingest PR"
finish ok "$TODO_COUNT meeting(s) distilled onto $INGEST_BRANCH"
