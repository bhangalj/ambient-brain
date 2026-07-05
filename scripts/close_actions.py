#!/usr/bin/env python3
"""Close the loop on completed actions.

Scans 00-inbox/actions.md for ticked items (`- [x]`). For any that carry a Slack
source (channel+ts embedded when the action was created), it adds a ✅ reaction to
the original message, then moves the line to a dated done-log. This is what makes
the inbox actionable rather than write-only.

Env: SLACK_USER_TOKEN (scope: reactions:write)
"""
from __future__ import annotations
import re
import sys
from datetime import datetime
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import config, vault  # noqa: E402

REACT = "https://slack.com/api/reactions.add"
DONE_LOG = vault.VAULT / "99-meta" / "actions-done.md"
META_RE = re.compile(r"<!--\s*src:(?P<src>\S+)(?P<kv>.*?)-->")


def kv(s: str) -> dict:
    return dict(re.findall(r"(\w+)=(\S+)", s))


def react(token: str, channel: str, ts: str, emoji: str = "white_check_mark") -> None:
    r = requests.post(REACT, headers={"Authorization": f"Bearer {token}"},
                      data={"channel": channel, "timestamp": ts, "name": emoji}, timeout=30)
    data = r.json()
    if not data.get("ok") and data.get("error") not in ("already_reacted",):
        print(f"  ! slack react failed: {data.get('error')}")


def main() -> None:
    if not vault.ACTIONS.exists():
        print("No action inbox yet.")
        return
    token = config.env("SLACK_USER_TOKEN", required=False)
    lines = vault.ACTIONS.read_text(encoding="utf-8").splitlines()
    keep, closed = [], []
    for ln in lines:
        if ln.strip().startswith("- [x]"):
            m = META_RE.search(ln)
            if m and m.group("src") == "slack" and token:
                meta = kv(m.group("kv"))
                if meta.get("channel") and meta.get("ts"):
                    react(token, meta["channel"], meta["ts"])
            closed.append(ln)
        else:
            keep.append(ln)
    if closed:
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        DONE_LOG.parent.mkdir(parents=True, exist_ok=True)
        with DONE_LOG.open("a", encoding="utf-8") as f:
            f.write(f"\n### Closed {stamp}\n" + "\n".join(closed) + "\n")
        vault.ACTIONS.write_text("\n".join(keep) + "\n", encoding="utf-8")
        vault.regenerate_dashboard()  # open-action count changed
    print(f"Closed {len(closed)} actions.")


if __name__ == "__main__":
    main()
