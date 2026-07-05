"""Transcript webhook receiver.

Flow:  Fathom  ──POST──►  /webhook/{provider}
         1. verify the Svix-style signature (webhook-id/timestamp/signature)
         2. normalize via the provider adapter
         3. commit the normalized transcript to 00-inbox/transcripts/ in your repo
            (GitHub Contents API) — which triggers ingest-transcripts.yml to clean it.

Deploy as a tiny always-on service (Render / Fly / Railway / a VPS). It holds no
vault state; it just translates + commits, so the "brain" stays fully in git.

Env:
  WEBHOOK_SECRETS   json map, e.g. {"fathom":"whsec_…"}  (from Fathom when you
                    create the webhook). Empty/missing -> verification skipped (dev only).
  GITHUB_TOKEN      fine-grained PAT with contents:write on the vault repo
  GITHUB_REPO       "owner/repo"
  GITHUB_BRANCH     default "main"
"""
from __future__ import annotations
import base64
import hashlib
import hmac
import json
import os
import time

import requests
from fastapi import FastAPI, Request, HTTPException

from adapters import base, fathom  # noqa: F401  (import registers adapters)

app = FastAPI(title="work-brain webhook")


def _secrets() -> dict:
    return json.loads(os.environ.get("WEBHOOK_SECRETS", "{}"))


def verify(secret: str, headers, raw: bytes) -> bool:
    """Svix scheme (Fathom): HMAC-SHA256 over id.timestamp.body."""
    if not secret:
        return True  # dev mode
    wid = headers.get("webhook-id", "")
    wts = headers.get("webhook-timestamp", "")
    wsig = headers.get("webhook-signature", "")
    if not (wid and wts and wsig):
        return False
    if abs(int(time.time()) - int(wts)) > 300:
        return False
    key = base64.b64decode(secret.split("_", 1)[1])
    signed = f"{wid}.{wts}.".encode() + raw
    expected = base64.b64encode(hmac.new(key, signed, hashlib.sha256).digest()).decode()
    for part in wsig.split(" "):
        provided = part.split(",", 1)[-1]  # strip "v1," version prefix
        if hmac.compare_digest(provided, expected):
            return True
    return False


def commit_to_repo(path: str, content: str, message: str) -> None:
    token = os.environ["GITHUB_TOKEN"]
    repo = os.environ["GITHUB_REPO"]
    branch = os.environ.get("GITHUB_BRANCH", "main")
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    body = {
        "message": message,
        "content": base64.b64encode(content.encode()).decode(),
        "branch": branch,
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }
    r = requests.put(url, headers=headers, json=body, timeout=30)
    if r.status_code == 409 or r.status_code >= 500:
        # branch moved under us / transient GitHub error: the Contents-API
        # equivalent of pull --rebase + retry once (DESIGN §5)
        time.sleep(2)
        r = requests.put(url, headers=headers, json=body, timeout=30)
    if r.status_code not in (200, 201):
        raise HTTPException(502, f"GitHub commit failed: {r.status_code} {r.text[:200]}")


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/webhook/{provider}")
async def receive(provider: str, request: Request):
    raw = await request.body()
    if not verify(_secrets().get(provider, ""), request.headers, raw):
        raise HTTPException(401, "signature verification failed")
    payload = json.loads(raw or b"{}")

    norm = base.normalize(provider, payload)
    # skip pings / payloads with no transcript yet (Fathom processes async)
    if not norm.get("segments") and not norm.get("summary"):
        return {"status": "ignored", "reason": "no content yet"}

    from datetime import datetime
    date = norm.get("date") or datetime.utcnow().strftime("%Y-%m-%d")
    slug = "".join(c if c.isalnum() else "-" for c in norm["title"].lower())[:50].strip("-")
    fname = f"00-inbox/transcripts/{date}-{slug}-{norm['external_id']}.json"
    commit_to_repo(fname, json.dumps(norm, indent=2, ensure_ascii=False),
                   f"transcript: {norm['title']} ({provider})")
    return {"status": "committed", "path": fname}
