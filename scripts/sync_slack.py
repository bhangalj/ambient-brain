#!/usr/bin/env python3
"""Weekly Slack sync.

Uses the search.messages API (user token) to gather everything you're involved
in: messages you sent, @mentions of you, and DMs — since the last run. It then:
  * writes a weekly interaction digest to 06-interactions/
  * logs feedback-flagged messages to 05-feedback/
  * pushes keyword-matched messages into the action inbox WITH the Slack
    channel+ts+permalink, so close_actions.py can react back on the source.

Why search.messages: without Enterprise Grid Discovery (admin-only), this is the
cleanest way to get "messages I'm involved in" with a normal user token.

Env:    SLACK_USER_TOKEN   (xoxp-…, scope: search:read; reactions:write for the
                            update loop in close_actions.py)
Config: slack.* in config.yaml
"""
from __future__ import annotations
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import config, state, vault  # noqa: E402

SEARCH = "https://slack.com/api/search.messages"


def search(token: str, query: str) -> list[dict]:
    out, page = [], 1
    while True:
        r = requests.get(
            SEARCH,
            params={"query": query, "count": 100, "page": page, "sort": "timestamp"},
            headers={"Authorization": f"Bearer {token}"},
            timeout=30,
        )
        data = r.json()
        if not data.get("ok"):
            raise SystemExit(f"Slack error for '{query}': {data.get('error')}")
        matches = data.get("messages", {}).get("matches", [])
        out.extend(matches)
        paging = data.get("messages", {}).get("paging", {})
        if page >= paging.get("pages", 1):
            break
        page += 1
    return out


def classify(text: str, cfg: dict) -> set[str]:
    low = text.lower()
    tags = set()
    for kw in cfg.get("action_keywords", []):
        if kw.lower() in low:
            tags.add("action")
    for kw in cfg.get("feedback_keywords", []):
        if kw.lower() in low:
            tags.add("feedback")
    return tags


def main() -> None:
    token = config.env("SLACK_USER_TOKEN")
    cfg = config.load().get("slack", {})
    st = state.load()

    days = cfg.get("lookback_days", 8)
    after = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    queries = [f"{q} after:{after}" for q in cfg.get("search_queries", ["from:@me"])]

    digest, feedback_lines, n_actions = [], [], 0
    for q in queries:
        for m in search(token, q):
            uid = f"{m.get('channel', {}).get('id')}:{m.get('ts')}"
            if state.seen(st, "slack", uid):
                continue
            state.mark_seen(st, "slack", uid)
            text = m.get("text", "")
            chan = m.get("channel", {}).get("name", "?")
            user = m.get("username", m.get("user", "?"))
            perma = m.get("permalink", "")
            digest.append(f"- **#{chan}** · {user}: {text[:200]}  [↗]({perma})")

            tags = classify(text, cfg)
            if "action" in tags:
                vault.add_action(
                    text[:140], "slack",
                    {"channel": m.get("channel", {}).get("id"), "ts": m.get("ts"),
                     "permalink": perma},
                )
                n_actions += 1
            if "feedback" in tags:
                feedback_lines.append(f"- {text[:300]} — #{chan}, {user} [↗]({perma})")

    week = datetime.now(timezone.utc).strftime("%G-W%V")
    if digest:
        vault.write_note(
            vault.VAULT / "06-interactions" / f"slack-{week}.md",
            {"type": "interactions", "source": "slack", "week": week,
             "count": len(digest)},
            "# Slack — week " + week + "\n\n" + "\n".join(digest),
        )
    if feedback_lines:
        vault.append_section(
            vault.VAULT / "05-feedback" / f"{datetime.now().year}.md",
            f"Slack {week}", feedback_lines,
        )
    state.save(st)
    print(f"Slack: {len(digest)} messages, {n_actions} actions, "
          f"{len(feedback_lines)} feedback items.")


if __name__ == "__main__":
    main()
