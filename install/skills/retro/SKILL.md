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
   `python3 <vault>/install/retro/extract.py --days <N> --out "$(git -C <vault> rev-parse --git-path retro/digest.md)"`
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
4. Check the vault first. If a rule already says it, the fix is to make that
   rule clearer, not to add a second one.

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
rule to a new section. Write nothing yet.

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
- The files changed, the branch and the commit.
- The proposals the user declined, one line each.

## 6. Clean up

Delete the digest file.
