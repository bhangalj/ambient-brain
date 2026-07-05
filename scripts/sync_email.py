#!/usr/bin/env python3
"""Weekly email sync (Gmail API).

Pulls recent sent + received mail, flags feedback-ish threads by keyword, and
logs them to 05-feedback/. Kept deliberately conservative: it summarises subject
+ snippet, not full bodies, to keep the vault readable.

Auth (one-time): create an OAuth "Desktop app" client in Google Cloud, enable
the Gmail API, run `python scripts/gmail_auth.py` locally to mint a refresh
token, then set:
    GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET, GMAIL_REFRESH_TOKEN
(For non-Gmail: swap this module for an IMAP version — same output contract.)
"""
from __future__ import annotations
import base64
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import config, state, vault  # noqa: E402

TOKEN_URL = "https://oauth2.googleapis.com/token"
GMAIL = "https://gmail.googleapis.com/gmail/v1/users/me"


def access_token() -> str:
    r = requests.post(TOKEN_URL, data={
        "client_id": config.env("GMAIL_CLIENT_ID"),
        "client_secret": config.env("GMAIL_CLIENT_SECRET"),
        "refresh_token": config.env("GMAIL_REFRESH_TOKEN"),
        "grant_type": "refresh_token",
    }, timeout=30)
    r.raise_for_status()
    return r.json()["access_token"]


def list_messages(tok: str, q: str) -> list[str]:
    ids, page = [], None
    while True:
        params = {"q": q, "maxResults": 100}
        if page:
            params["pageToken"] = page
        r = requests.get(f"{GMAIL}/messages", params=params,
                         headers={"Authorization": f"Bearer {tok}"}, timeout=30)
        r.raise_for_status()
        data = r.json()
        ids += [m["id"] for m in data.get("messages", [])]
        page = data.get("nextPageToken")
        if not page:
            return ids


def get_message(tok: str, mid: str) -> dict:
    r = requests.get(f"{GMAIL}/messages/{mid}",
                     params={"format": "metadata",
                             "metadataHeaders": ["Subject", "From", "To", "Date"]},
                     headers={"Authorization": f"Bearer {tok}"}, timeout=30)
    r.raise_for_status()
    return r.json()


def header(msg: dict, name: str) -> str:
    for h in msg.get("payload", {}).get("headers", []):
        if h["name"].lower() == name.lower():
            return h["value"]
    return ""


def main() -> None:
    cfg = config.load().get("email", {})
    tok = access_token()
    st = state.load()

    days = cfg.get("lookback_days", 8)
    kw = " OR ".join(cfg.get("feedback_keywords", ["feedback", "great job", "concern"]))
    query = f'newer_than:{days}d ({kw})'

    lines = []
    for mid in list_messages(tok, query):
        if state.seen(st, "email", mid):
            continue
        state.mark_seen(st, "email", mid)
        msg = get_message(tok, mid)
        subj = header(msg, "Subject") or "(no subject)"
        frm = header(msg, "From")
        snippet = msg.get("snippet", "")[:280]
        lines.append(f"- **{subj}** — {frm}\n  > {snippet}")

    if lines:
        week = datetime.now(timezone.utc).strftime("%G-W%V")
        vault.append_section(
            vault.VAULT / "05-feedback" / f"{datetime.now().year}.md",
            f"Email {week}", lines,
        )
        vault.regenerate_dashboard()  # dashboard inputs changed
    state.save(st)
    print(f"Email: logged {len(lines)} feedback-flagged threads.")


if __name__ == "__main__":
    main()
