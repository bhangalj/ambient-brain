---
name: retro
description: Run a transcript retro on the brain vault. Use when the user says "/retro", "run a retro", or "what did you keep getting wrong this week". Mines recent Claude Code session transcripts for repeated corrections, interrupts, rejected calls and tool errors, proposes concrete edits to the vault's rules, skills and topic pages, and applies only the edits the user approves. Claude Code only.
---

# /retro: turn last week's mistakes into rules

The vault is the `__VAULT_DIR__` path in the "Ambient Brain" block of
`~/.claude/CLAUDE.md` (default `~/brain`). Read `<vault>/AGENTS.md` once per
session before you write.

This skill reads Claude Code transcripts (`~/.claude/projects/`) only. Other
harnesses do not write them, so they skip this skill.

## 1. Extract

1. The window is 7 days unless the user names another. The script clamps it
   to 30 days, because Claude Code by default deletes transcripts older than 30
   days (`cleanupPeriodDays`).
2. Create the directory, then run the script:
   `mkdir -p "$(dirname "$(git -C <vault> rev-parse --git-path retro/digest.md)")"`
   `python3 <vault>/install/skills/retro/scripts/extract.py --days <N> --out "$(git -C <vault> rev-parse --git-path retro/digest.md)"`
   The digest holds private session content. It goes under `.git/`, so git
   never tracks it. Never write it, or any part of it, anywhere in the tree.
3. Read the digest. If it starts with "Too few signals", tell the user and
   offer a wider window. Stop if they decline.

## 2. Find the lessons

1. Corrections are a keyword match. Read the assistant turn before each one.
   Discard the ones that are not pushback.
2. A lesson needs a pattern: the same correction, error or rejection in 2 or
   more sessions, or 1 correction the user had to repeat. One-off mistakes are
   not lessons.
3. Sort each lesson into one kind:
   - a rule the agent broke or keeps forgetting;
   - a tool gotcha (an error shape, or a command that failed and was re-run);
   - a skill step that is wrong, missing or unclear;
   - a fact the agent had to be told more than once.
4. Check the vault first. If a rule already says it, never add a second copy.
   Make an unclear rule clearer. A clear rule that is still broken needs
   enforcement: list it as a hook candidate (step 3).
5. Read the review findings sections. They cover subagents whose type names
   "review". A `repeat:` bucket in 3 or more sessions is a mistake that repeats
   across sessions. Buckets and severities are keyword matches, so read the
   Blocking sample before you trust a bucket. Find the rule that covers it in
   the review-loop rules (a skill or the snippet). If the rule exists
   and the bucket still repeats, sharpen the review-loop rules. Never add a
   second copy. Blocking counts that stay flat after round 2 point at the
   review-loop rules.

## 3. Propose

For each lesson, show the user one proposal:

- **Lesson**: one line.
- **Evidence**: the count, and at most one short quoted line. Run it through
  the redaction list in `AGENTS.md` → "Never store" first.
- **Edit**: the target file and the exact text to add or change. Targets:
  `AGENTS.md`, `install/skills/*/SKILL.md` (and their `references/`),
  `install/claude-md-snippet.md`, or a `topics/<slug>.md` page (for example a
  `topics/cli-<tool>.md` gotcha).

Keep each edit as small as the lesson. Prefer a sharper line in an existing
rule to a new section.

Also propose at least one **retirement** per run: a rule, gotcha or skill step
to delete or shorten. Propose it only when the vault proves one of these:

- a hook now enforces the rule, so the text can shrink to one line that names
  the hook;
- a later rule supersedes or contradicts it;
- the same rule is on two pages;
- it describes a bug, tool or version that the vault records as fixed or gone.

Never retire a safety rail, the never-store rule, or a rule only because
nobody broke it this week. If nothing meets the bar, show the three closest
candidates, each with the proof it lacks.

Then list the **hook candidates**: Claude Code PreToolUse or UserPromptSubmit
hooks that would catch a pattern every time. For each, give the event and
matcher, what it detects, what it does (block with a message, or add context),
and the evidence. Write no hook in this run.

Write nothing yet.

## 4. Apply what the user approves

1. Apply only the proposals the user approves, as they approved them.
2. Vault with a remote (`git -C <vault> remote` prints something): run
   `git -C <vault> switch -c retro/YYYY-MM-DD` (today; add `-2`, `-3` and so
   on if the name exists) before you commit. Never push unless the user asks.
   Local-only vault: commit on the current branch.
3. Commit per `remember/SKILL.md` step 5, steps 3 and 4: stage only the paths
   you edited, then check `git -C <vault> diff --cached --name-only`.
4. `git -C <vault> commit -m "retro: <summary>"`. On a retro branch, then run
   `git -C <vault> switch -` to return to the original branch.
5. An edit to `install/claude-md-snippet.md` reaches `~/.claude/CLAUDE.md`
   only by hand, because `bootstrap.sh` leaves an existing block alone. Say so.

## 5. Report

- The lessons found, and which the user approved.
- The retirements proposed, and the hook candidates.
- The files changed, the branch and the commit.
- The proposals the user declined, one line each.

## 6. Clean up

Delete the digest file.
