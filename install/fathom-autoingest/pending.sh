#!/usr/bin/env bash
#
# Fathom auto-ingest — pending-work reporter for the Claude Code SessionStart hook.
#
# This is the ONLY thing that makes an unreviewed ingest visible, so it has two
# jobs, not one:
#   1. tell you a distillation is sitting on a branch waiting to be merged
#   2. tell you the automation itself is broken or has gone quiet
# A cron that dies silently is indistinguishable from a cron with nothing to do,
# and the second failure is the one that costs you a fortnight of meetings.
#
# Runs on EVERY session start, so it is local-git only — no network, no `gh`,
# no API call. Silent when there is nothing to say: whatever it prints lands in
# the model's context, so noise here is noise in every conversation.

set -uo pipefail

VAULT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." 2>/dev/null && pwd)" || exit 0
[ -d "$VAULT/.git" ] || exit 0

INGEST_BRANCH="fathom-ingest"
STATUS_FILE="$VAULT/.git/fathom-autoingest.status"
PR_FILE="$VAULT/.git/fathom-autoingest.pr"
STALE_DAYS=3

git() { command git -C "$VAULT" "$@"; }

# Everything below prints into `report`, which is captured rather than sent
# straight to stdout. A bare SessionStart hook's stdout reaches the MODEL only —
# the vault owner never saw any of it. Emitting JSON with `systemMessage` puts
# the same text in front of the human in Claude Code, which is now the only
# place this surfaces at all: run.sh's macOS banner was removed for the same
# reason.
report() {

# ------------------------------------------------- 1. pending distillation ---
if git show-ref --verify --quiet "refs/heads/$INGEST_BRANCH"; then
  # Gate on CONTENT, never on the commit graph. A squash-merge lands this
  # branch's work on main under a NEW commit id, and run.sh merges main back into
  # the branch on every run, so `rev-list --count main..branch` stays non-zero
  # for ever on a branch that has nothing left to give. `git diff main..branch`
  # is no better by itself: it reports a file that differs in EITHER direction,
  # so a note that reached main by another route, and was never on the branch at
  # all, still counts as pending.
  #
  # Both mistakes have fired together in practice: this banner demanded a merge
  # of an ingest PR carrying nothing — "1 meeting note(s) pending review" for a
  # branch whose patch against main added zero lines, where the note it counted
  # was the one sitting on MAIN and missing from the branch. Ask the only
  # question that matters instead — what would this branch ADD to main?
  ADDED="$(git diff "main..$INGEST_BRANCH" 2>/dev/null | grep -c '^+[^+]')"
  if [ "${ADDED:-0}" -gt 0 ]; then
    # numstat is "added deleted path": keep only meeting notes the branch really
    # adds lines to, so a note main is ahead on is never counted as pending.
    NOTE_FILES="$(git diff --numstat "main..$INGEST_BRANCH" -- meetings/ 2>/dev/null \
                  | awk '$1 ~ /^[0-9]+$/ && $1 > 0 && $3 ~ /^meetings\/20/ { print $3 }')"
    NOTES="$(printf '%s' "$NOTE_FILES" | grep -c .)"
    DAYS="$(printf '%s\n' "$NOTE_FILES" \
            | sed -n 's#^meetings/\([0-9-]\{10\}\).*#\1#p' | sort -u | tr '\n' ' ')"
    # A partial or notes-free distillation is still pending work, so say what is
    # actually there rather than reporting "0 meeting note(s)".
    if [ "${NOTES:-0}" -gt 0 ]; then
      SUBJECT="$NOTES meeting note(s)"
    else
      SUBJECT="$(git rev-list --count "main..$INGEST_BRANCH" 2>/dev/null || echo 0) commit(s), no new meeting notes"
    fi
    printf '⚠ Fathom ingest pending review: %s on branch `%s`' "$SUBJECT" "$INGEST_BRANCH"
    [ -n "$DAYS" ] && printf ' (%s)' "${DAYS% }"
    printf '.\n'
    [ -s "$PR_FILE" ] && printf '  PR: %s\n' "$(cat "$PR_FILE")"
    # Spell the merge out in full: a bare `gh pr merge` reads the CURRENT branch
    # (main, always, by the time you see this) and picks up the ACTIVE gh
    # account, which on a multi-account machine is not the vault owner
    # (AGENTS.md, "Git auth on multi-account machines").
    #
    # `gh pr ready` first, because run.sh opens these as DRAFT PRs and
    # `gh pr merge` refuses one outright: "Pull Request is still a draft". The
    # command printed here is the only instruction this banner exists to give,
    # and without `pr ready` it cannot work on a fresh ingest.
    #
    # Separated by `;` and not `&&`: `gh pr ready` exits 1 on a PR that is
    # ALREADY ready, printing "Only draft pull requests can be marked as ready",
    # which under `&&` would abort the merge it was meant to enable. stderr is
    # dropped so that no-op does not read as a failure. This script is local-git
    # only by design (no network, no gh, runs on every session start), so it
    # cannot look up which state the PR is in — the one line it prints has to be
    # correct for both.
    GH_OWNER="$(git remote get-url origin 2>/dev/null | sed -nE 's#.*github\.com[:/]([^/]+)/.*#\1#p')"
    MERGE_CMD="gh pr ready $INGEST_BRANCH 2>/dev/null; gh pr merge $INGEST_BRANCH --squash --delete-branch"
    # Subshell + export, so the token reaches BOTH gh calls while staying out of
    # the terminal this gets pasted into — a leaked GH_TOKEN would silently pin
    # every later gh command in that shell to the vault owner.
    [ -n "$GH_OWNER" ] && MERGE_CMD="( export GH_TOKEN=\"\$(gh auth token --user $GH_OWNER)\"; $MERGE_CMD )"
    printf '  Merge with: cd %s && %s\n' "$VAULT" "$MERGE_CMD"
  fi
fi

# ------------------------------------------------------- 2. health of the job -
if [ -f "$STATUS_FILE" ]; then
  IFS=$'\t' read -r STATE WHEN MSG <"$STATUS_FILE"
  if [ "${STATE:-}" = "error" ]; then
    printf '⚠ Fathom auto-ingest last run FAILED (%s): %s\n' "${WHEN:-?}" "${MSG:-unknown}"
    printf '  Log: ~/Library/Logs/fathom-autoingest.log\n'
  elif [ -n "$(find "$STATUS_FILE" -maxdepth 0 -mtime "+$STALE_DAYS" 2>/dev/null)" ]; then
    # Covers two shapes of dead: never fired at all, and fired on schedule but
    # deferred every time (run.sh deliberately stops refreshing this file while
    # it keeps deferring, so the mtime is the age of the FIRST deferral).
    printf '⚠ Fathom auto-ingest has not completed a run since %s — last status: %s (%s).\n' \
      "${WHEN:-?}" "${STATE:-?}" "${MSG:-no detail}"
    printf '  Check: launchctl list | grep fathom\n'
  fi
else
  # No status file at all: either never installed, or installed and never fired.
  if [ -f "$HOME/Library/LaunchAgents/com.ambient-brain.fathom-autoingest.plist" ]; then
    printf '⚠ Fathom auto-ingest is installed but has never run. Check: launchctl list | grep fathom\n'
  fi
fi

}

# ------------------------------------------------------------------ emit -----
OUT="$(report)"
[ -z "$OUT" ] && exit 0

# `systemMessage` renders to you; `additionalContext` reaches the model, so an
# agent can act on a pending merge without being told. Same text, both places.
#
# python3 does the escaping because the merge command carries double quotes and
# a `$(...)`, which hand-rolled sed escaping gets wrong. Message goes via the
# environment, never interpolated into the -c source. If python3 is missing the
# script falls back to plain stdout — model-only, but never silent.
if command -v python3 >/dev/null 2>&1; then
  MSG="$OUT" python3 -c 'import json, os, sys
m = os.environ["MSG"].rstrip("\n")
json.dump({
    "systemMessage": m,
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": m,
    },
}, sys.stdout)
' || printf '%s\n' "$OUT"
else
  printf '%s\n' "$OUT"
fi

exit 0
