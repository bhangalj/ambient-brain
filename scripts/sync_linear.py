#!/usr/bin/env python3
"""Weekly Linear sync.

Pulls issues you're assigned to or subscribed to that changed since the last run,
writes one note per issue under 02-projects/<project>/tasks/, logs completed
issues to the project's done.md, and refreshes each touched project's digest
plus DASHBOARD.md (§6).

Env:  LINEAR_API_KEY   (Settings > API > Personal API key)
"""
from __future__ import annotations
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import config, state, vault  # noqa: E402

API = "https://api.linear.app/graphql"

VIEWER_Q = "{ viewer { id name } }"

ISSUES_Q = """
query($after: DateTimeOrDuration, $cursor: String) {
  issues(
    first: 50
    after: $cursor
    filter: {
      updatedAt: { gt: $after }
      or: [
        { assignee: { isMe: { eq: true } } }
        { subscribers: { some: { isMe: { eq: true } } } }
      ]
    }
    orderBy: updatedAt
  ) {
    pageInfo { hasNextPage endCursor }
    nodes {
      id identifier title url updatedAt completedAt
      state { name type }
      priorityLabel
      project { name }
      description
    }
  }
}
"""


def gql(key: str, query: str, variables: dict | None = None) -> dict:
    r = requests.post(
        API,
        json={"query": query, "variables": variables or {}},
        headers={"Authorization": key, "Content-Type": "application/json"},
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    if "errors" in data:
        raise SystemExit(f"Linear API error: {data['errors']}")
    return data["data"]


def issue_note(issue: dict) -> str:
    project = issue.get("project") or {}
    project_name = project.get("name") or "No Project"
    pslug = vault.slugify(project_name)
    tasks_dir = vault.VAULT / "02-projects" / pslug / "tasks"
    meta = {
        "type": "task",
        "source": "linear",
        "id": issue["identifier"],
        "title": issue["title"],
        "status": (issue.get("state") or {}).get("name"),
        "state_type": (issue.get("state") or {}).get("type"),
        "priority": issue.get("priorityLabel"),
        "project": f"[[{pslug}/_project|{project_name}]]",
        "url": issue["url"],
        "updated": issue["updatedAt"],
        "completed": issue.get("completedAt"),
    }
    body = (issue.get("description") or "_No description._").strip()
    vault.write_note(tasks_dir / f"{issue['identifier']}.md", meta, body)
    # completed work gets logged as documentation (§8: completed -> done.md)
    if (issue.get("state") or {}).get("type") == "completed":
        vault.append_section(
            vault.VAULT / "02-projects" / pslug / "done.md",
            "Completed",
            [f"- [[tasks/{issue['identifier']}|{issue['identifier']}]] {issue['title']}"],
        )
    return pslug


def main() -> None:
    key = config.env("LINEAR_API_KEY")
    st = state.load()
    since = state.get_cursor(st, "linear", "P7D")  # default: last 7 days
    viewer = gql(key, VIEWER_Q)["viewer"]
    print(f"Linear viewer: {viewer['name']}")

    cursor, count, latest = None, 0, ""  # latest: real timestamps only, never 'P7D'
    touched: set[str] = set()
    while True:
        data = gql(key, ISSUES_Q, {"after": since, "cursor": cursor})["issues"]
        for issue in data["nodes"]:
            if state.seen(st, "linear", issue["id"] + issue["updatedAt"]):
                continue
            # projectless issues land in no-project/ — it needs a _project.md
            # too, or digest/dashboard/lint silently skip those tasks (§6)
            vault.ensure_project((issue.get("project") or {}).get("name")
                                 or "No Project")
            touched.add(issue_note(issue))
            state.mark_seen(st, "linear", issue["id"] + issue["updatedAt"])
            latest = max(latest or "", issue["updatedAt"])
            count += 1
        if not data["pageInfo"]["hasNextPage"]:
            break
        cursor = data["pageInfo"]["endCursor"]

    if latest:
        state.set_cursor(st, "linear", latest)
    state.save(st)
    if count:  # digest invariant (§6): leave every touched project + dashboard current
        for slug in sorted(touched):
            vault.refresh_digest(slug)
        vault.regenerate_dashboard()
    print(f"Linear: wrote/updated {count} issue notes.")


if __name__ == "__main__":
    main()
