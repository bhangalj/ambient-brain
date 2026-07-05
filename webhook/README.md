# Transcript webhook receiver

A tiny always-on service that receives meeting-transcript webhooks (Fathom today,
anything tomorrow), verifies them, and commits a normalized transcript into
`00-inbox/transcripts/` in your vault repo. The `ingest-transcripts.yml` Action
then cleans + wiki-links it. The service holds no state — the brain stays in git.

## Run locally

```bash
cd webhook
pip install -r requirements.txt
export GITHUB_TOKEN=... GITHUB_REPO=you/work-brain GITHUB_BRANCH=main
export WEBHOOK_SECRETS='{}'        # empty = skip signature check (dev only)
uvicorn app:app --port 8000
# expose it: ngrok http 8000   (grab the https URL)
```

## Deploy (pick one)

Render / Railway / Fly.io all work; it's one container. Set the env vars below,
deploy, and use the public `https://…/webhook/fathom` URL.

```
GITHUB_TOKEN     fine-grained PAT, contents:write on the vault repo
GITHUB_REPO      owner/repo
GITHUB_BRANCH    main
WEBHOOK_SECRETS  {"fathom":"whsec_…"}   # the secret Fathom shows on webhook creation
ANTHROPIC_API_KEY  (not needed here — cleaning runs in CI)
```

## Point Fathom at it

Fathom → Settings → **API Access** → Generate API key → **Add Webhook**:
- Destination URL: `https://your-service/webhook/fathom`
- Tick **Summary**, **Action items**, **Transcript**
- Scope: `my_recordings` (and `shared_with_me` if you want those too)

Fathom signs each request (`webhook-id` / `webhook-timestamp` / `webhook-signature`,
HMAC-SHA256 over `id.timestamp.body`, `whsec_` secret). `app.py` verifies this.
Test with Fathom's **Send Test Payload** button or a 2-minute recording.

## Add another provider

Drop `adapters/<name>.py` with an `@register("<name>")` function that maps the
payload to the normalized shape in `adapters/base.py`, import it in `app.py`, and
POST to `/webhook/<name>`. No other changes.
