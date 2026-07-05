#!/usr/bin/env python3
"""One-time helper: mint a Gmail refresh token for sync_email.py.

Prereqs:
  1. Google Cloud console -> create project -> enable the Gmail API.
  2. OAuth consent screen -> add yourself as a test user.
  3. Credentials -> Create OAuth client ID -> "Desktop app". Note the client
     id + secret.

Run:
  GMAIL_CLIENT_ID=... GMAIL_CLIENT_SECRET=... python scripts/gmail_auth.py

It prints a URL, you paste the code back, and it prints GMAIL_REFRESH_TOKEN.
Add that (plus id/secret) to your .env and GitHub Actions secrets. Read-only scope.
"""
from __future__ import annotations
import os
import urllib.parse
import webbrowser

import requests

SCOPE = "https://www.googleapis.com/auth/gmail.readonly"
AUTH = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN = "https://oauth2.googleapis.com/token"
REDIRECT = "urn:ietf:wg:oauth:2.0:oob"  # manual copy/paste flow


def main() -> None:
    cid = os.environ["GMAIL_CLIENT_ID"]
    secret = os.environ["GMAIL_CLIENT_SECRET"]
    params = urllib.parse.urlencode({
        "client_id": cid, "redirect_uri": REDIRECT, "response_type": "code",
        "scope": SCOPE, "access_type": "offline", "prompt": "consent",
    })
    url = f"{AUTH}?{params}"
    print("Open this URL, approve, and paste the code back:\n", url, "\n")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    code = input("code> ").strip()
    r = requests.post(TOKEN, data={
        "code": code, "client_id": cid, "client_secret": secret,
        "redirect_uri": REDIRECT, "grant_type": "authorization_code",
    }, timeout=30)
    r.raise_for_status()
    tok = r.json()
    print("\nGMAIL_REFRESH_TOKEN=" + tok["refresh_token"])


if __name__ == "__main__":
    main()
