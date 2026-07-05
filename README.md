# work-brain — a git-backed Obsidian workOS

A work-only second brain. Markdown notes in an Obsidian vault, versioned in git,
kept current by scheduled syncs (Linear, Slack, email), fast local ingest
(meeting transcripts, dictated brain-dumps), and a Claude Code session-end hook.

## The idea in one picture

```
                 weekly (GitHub Actions cron)          fast/local (cron or hook)
                 ─────────────────────────────         ──────────────────────────
  Linear  ─┐                                   00-inbox/transcripts ─┐
  Slack   ─┼─► sync_*.py ─► notes + digests    dictated dumps ───────┼─► ingest / router
  Email   ─┘                    │                                    │        │
                                ▼                                    ▼        ▼
                        ┌───────────────────  the vault  ───────────────────────┐
                        │ 02-projects  03-meetings  05-feedback  06-interactions │
                        │ 00-inbox/actions.md  ← keyword hits, carry Slack msg id │
                        └───────────────────────┬────────────────────────────────┘
                                                │  tick a box → close_actions.py
                                                ▼  reacts ✅ in Slack, archives it
                                          Semantic search (Obsidian plugin) over it all
```

Everything is plain markdown, so the "semantic search / LLM wiki" layer is an
Obsidian plugin over the vault — **Smart Connections** or **Copilot** (local
embeddings + chat). No separate vector DB to run.

## Vault layout

| Folder | Holds |
|---|---|
| `00-inbox/actions.md` | todo inbox; each item embeds its Slack `channel`+`ts` for the update loop |
| `00-inbox/transcripts/` | drop meeting transcripts here; `ingest_transcript.py` drains it |
| `00-inbox/braindumps/` | optional landing spot for dictated dumps |
| `01-daily/` | daily notes (dumps default here) |
| `02-projects/<slug>/` | `_project.md` + `tasks/` (Linear issues) + completed-work log |
| `03-meetings/` | cleaned, wiki-linked meeting notes (raw kept in `_raw/`) |
| `04-people/` | one note per colleague; interactions link here |
| `05-feedback/` | positive + negative feedback from Slack/email |
| `06-interactions/` | weekly Slack digests |
| `07-reference/` | durable docs / knowledge |
| `99-meta/` | `sync-state.json` (cursors + dedup), done-log |

## What runs when

| Cadence | Runs | Mechanism |
|---|---|---|
| Weekly | `sync_linear.py`, `sync_slack.py`, `sync_email.py` | GitHub Actions cron (`.github/workflows/weekly-sync.yml`) |
| Per meeting | Fathom → `webhook/` receiver commits raw → `ingest-transcripts.yml` cleans + wiki-links it | webhook push → GitHub Action |
| On demand | `braindump_router.py` (`/braindump` in Claude Code), `close_actions.py` | local / hook |
| End of Claude session | `session_capture.py` → drains any local inbox, closes actions, commits + pushes | `.claude/settings.json` `SessionEnd` hook |

Transcripts are hands-off: Fathom posts to the receiver the moment a meeting is
processed, the receiver commits a normalized file, and the push-triggered Action
cleans it. Swap Fathom for any provider by adding one adapter — see `webhook/README.md`.

The heavy syncs run in CI so they don't depend on your laptop being awake. The
latency-sensitive, LLM-driven bits (transcripts, dumps) run locally where your
`ANTHROPIC_API_KEY` and files live.

## Setup

1. **Vault**: open this folder in Obsidian. Install **Smart Connections** (or
   Copilot) for semantic search; point Templater at `templates/`.
2. **Git**: `git init && git add -A && git commit -m init`, push to a *private* repo.
3. **Config**: `cp config.example.yaml config.yaml`, set your Slack handle in
   `search_queries`, tune keyword lists.
4. **Secrets**: `cp .env.example .env` for local; add the same as GitHub Actions
   secrets for CI. Tokens/scopes below.
5. **Claude Code**: merge `.claude/settings.example.json` into your
   `.claude/settings.json`. `/braindump <text>` routes a dictated dump.

### Tokens & scopes

- **Linear** — Settings → API → personal key → `LINEAR_API_KEY`.
- **Slack** — user token (`xoxp-…`) with `search:read` (sync) and `reactions:write`
  (the close-the-loop reaction). `search.messages` needs a *user* token; a bot
  token won't work. Full-firehose ingestion would need Enterprise Grid Discovery
  (admin-only) — the search approach is the no-admin path.
- **Gmail** — OAuth desktop client + Gmail API; mint a refresh token once. Non-Gmail:
  replace `sync_email.py` with an IMAP version keeping the same output.
- **Anthropic** — `ANTHROPIC_API_KEY` for transcript cleaning + dump routing.

## The action-inbox loop

When a sync sees an action-keyword message, it appends to `00-inbox/actions.md`:

```
- [ ] review the DPA draft  (from slack, 2026-07-04) <!-- src:slack channel=C0ABC ts=1720099999.001 permalink=https://… -->
```

Tick the box, and `close_actions.py` reads the embedded id, adds ✅ to the
original Slack message, and moves the line to `99-meta/actions-done.md`. That
`channel`+`ts` pair *is* the update-loop handle you asked for.

## Extending

- New source → new `sync_*.py` using `lib/state` (dedup) + `lib/vault` (writing);
  add a step to the workflow.
- Different transcript tool → just export into `00-inbox/transcripts/`; the
  ingester is format-agnostic (`.txt .md .vtt .srt .json`).
- Prefer local-only (no CI) → run the same scripts from `cron`; nothing is
  GitHub-specific except the workflow file.
