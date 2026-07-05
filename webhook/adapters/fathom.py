"""Fathom -> normalized transcript.

Fathom's payload can include summary, transcript, and action_items depending on
how the webhook was created (scopes + include_* flags). Field names vary a little
across Fathom's API versions, so this maps the common keys defensively and keeps
the raw payload around for anything unmapped.
"""
from __future__ import annotations

from .base import register


def _segments(payload: dict) -> list[dict]:
    tr = payload.get("transcript") or payload.get("transcript_segments") or []
    # transcript may be a list of segments, or a dict with 'segments', or a string
    if isinstance(tr, dict):
        tr = tr.get("segments", [])
    if isinstance(tr, str):
        return [{"speaker": "", "text": tr, "ts": ""}]
    out = []
    for s in tr:
        if not isinstance(s, dict):
            continue
        out.append({
            "speaker": s.get("speaker") or s.get("speaker_name") or s.get("name") or "",
            "text": s.get("text") or s.get("content") or "",
            "ts": str(s.get("timestamp") or s.get("start") or s.get("ts") or ""),
        })
    return out


def _attendees(payload: dict) -> list[str]:
    people = payload.get("participants") or payload.get("attendees") or []
    out = []
    for p in people:
        if isinstance(p, str):
            out.append(p)
        elif isinstance(p, dict):
            name = p.get("name") or p.get("display_name") or ""
            email = p.get("email") or ""
            out.append(f"{name} <{email}>".strip() if email else name)
    return [a for a in out if a]


def _actions(payload: dict) -> list[dict]:
    items = payload.get("action_items") or []
    out = []
    for a in items:
        if isinstance(a, str):
            out.append({"owner": "", "task": a})
        elif isinstance(a, dict):
            out.append({
                "owner": a.get("assignee") or a.get("owner") or "",
                "task": a.get("text") or a.get("description") or a.get("task") or "",
            })
    return out


@register("fathom")
def fathom(payload: dict) -> dict:
    meeting = payload.get("meeting") or payload  # some payloads nest under 'meeting'
    rec_id = str(payload.get("recording_id") or meeting.get("id")
                 or meeting.get("recording_id") or "")
    title = meeting.get("title") or meeting.get("meeting_title") or "Fathom Meeting"
    date = None
    for k in ("scheduled_start_time", "started_at", "date", "created_at", "meeting_start"):
        if meeting.get(k):
            date = str(meeting[k])[:10]
            break
    summary = payload.get("summary") or meeting.get("summary")
    if isinstance(summary, dict):
        summary = summary.get("markdown") or summary.get("text")
    return {
        "provider": "fathom",
        "external_id": rec_id or (date or "") + "-" + title,
        "title": title,
        "date": date,
        "attendees": _attendees(meeting),
        "segments": _segments(payload),
        "summary": summary,
        "action_items": _actions(payload),
        "url": (payload.get("meeting_url") or payload.get("url")
                or payload.get("share_url") or meeting.get("url")),
    }
