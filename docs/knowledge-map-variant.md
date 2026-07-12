# Variant: project knowledge map (companion repo)

The brain pattern also works scoped to a single system — a "knowledge map"
living INSIDE a project repo (e.g. `docs/org-map/` in a Salesforce DX repo, an
infrastructure repo, a data-warehouse repo). Same bones, different contract:
the brain remembers *you*; a knowledge map explains *one system* to any agent
session working on it.

## What stays the same
- Entity pages + a lean `_index.md` (one terse line per page, capped)
- Stable kebab-case slugs, cross-links, frontmatter with `updated`
- Never-store rule (document WHERE secrets live, never their values)
- Dated, immutable snapshots for anything derived from a live system

## What changes

| | Brain | Knowledge map |
|---|---|---|
| Consumer | you + any agent, anywhere | agent sessions working THIS repo |
| Entry point | global CLAUDE.md snippet | the repo's own CLAUDE.md, referencing every map page |
| Verbs | `/remember` `/recall` `/lint` skills | no skills — CLAUDE.md carries the contract (repo-scoped skills optional, later, if earned) |
| Content | judgment, intent, history, preferences | structure and mechanics, regenerable from the system |
| Freshness | lint sweeps | verified-dates + a repo hook + regen scripts |

## The storage-split razor
For each fact, ask in order:
1. **Could a script regenerate it?** → generated artifact / map page in this repo.
2. **Could one command answer it?** → don't store it; derive live when needed.
3. **Is it judgment, history, intent, "what breaks if"?** → it belongs in the
   BRAIN, not the map — put a cross-reference in the map page instead.

The failure mode this prevents: an agent derives a system's *mechanics*
perfectly and still draws the wrong conclusion because the *intent* wasn't
written anywhere. Mechanics go here; intent goes to the brain.

## Keeping the map honest
- Every page carries a `verified: YYYY-MM-DD` line and cites the source
  metadata paths / commands used to derive it.
- Add a repo hook (e.g. pre-commit on the metadata/source dirs) that flags:
  "you changed X — update or re-verify its map page."
- Prefer a small regen script for the mechanical layers (object/field
  inventories, relationship graphs); LLM-written prose only for behavior
  summaries a script can't produce.
- Survey broadly first (e.g. all automations + metadata together), group into
  topic clusters, THEN fan out subagents per cluster — don't fan out blind.
