#!/usr/bin/env python3
"""Weekly Linear sync.

Pulls issues you're assigned to or subscribed to that changed since the last run,
writes one note per issue under 02-projects/<project>/tasks/, and refreshes a
status rollup in each project's _project.md.

Env:  LINEAR_API_KEY   (Settings > API > Personal API key)
"""
from __future__ import annotations
import sys
from datetime import datetime, timezone
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
    filter: { updatedAt: { gt: $after }, assignee: { isMe: { eq: true } } }
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


def issue_note(issue: dict) -> None:
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
    # completed work gets logged as documentation
    if (issue.get("state") or {}).get("type") == "completed":
        vault.append_section(
            vault.VAULT / "02-projects" / pslug / "_project.md",
            "Completed",
            [f"- [[tasks/{issue['identifier']}|{issue['identifier']}]] {issue['title']}"],
        )


def ensure_project_note(project_name: str) -> None:
    pslug = vault.slugify(project_name)
    path = vault.VAULT / "02-projects" / pslug / "_project.md"
    if not path.exists():
        vault.write_note(
            path,
            {"type": "project", "name": project_name, "status": "active",
             "created": datetime.now(timezone.utc).strftime("%Y-%m-%d")},
            f"# {project_name}\n\nOverview of the project, its goal, and links.\n",
        )


def main() -> None:
    key = config.env("LINEAR_API_KEY")
    st = state.load()
    since = state.get_cursor(st, "linear", "P7D")  # default: last 7 days
    viewer = gql(key, VIEWER_Q)["viewer"]
    print(f"Linear viewer: {viewer['name']}")

    cursor, count, latest = None, 0, since
    while True:
        data = gql(key, ISSUES_Q, {"after": since, "cursor": cursor})["issues"]
        for issue in data["nodes"]:
            if state.seen(st, "linear", issue["id"] + issue["updatedAt"]):
                continue
            if issue.get("project"):
                ensure_project_note(issue["project"]["name"])
            issue_note(issue)
            state.mark_seen(st, "linear", issue["id"] + issue["updatedAt"])
            latest = max(latest or "", issue["updatedAt"])
            count += 1
        if not data["pageInfo"]["hasNextPage"]:
            break
        cursor = data["pageInfo"]["endCursor"]

    if latest and latest != "P7D":
        state.set_cursor(st, "linear", latest)
    state.save(st)
    print(f"Linear: wrote/updated {count} issue notes.")


if __name__ == "__main__":
    main()
