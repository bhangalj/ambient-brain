#!/usr/bin/env python3
"""Transcript retro: mine Claude Code session transcripts for lessons. Stdlib only, no LLM.

Reads <claude dir>/projects/*/*.jsonl (and their subagents) modified in the last
--days days and writes a compact, redacted markdown digest of the signals worth
a lesson: user corrections, interrupts, rejected tool calls, grouped tool
errors and failed-then-retried commands. Prints one JSON line of stats to stderr.
The claude dir is $CLAUDE_CONFIG_DIR, default ~/.claude.

The digest holds private session content. Keep it out of the vault tree.

Claude Code transcript format, as observed (not a published schema):
  - a typed prompt is type=user with origin.kind=human (older records carry no
    origin); skill bodies (isMeta), task notifications, local-command echoes
    and headless `claude -p` prompts (promptSource=sdk) are not;
  - an interrupt is a user text block "[Request interrupted by user...]";
  - a rejected tool call is a tool_result with toolDenialKind=user-rejected,
    plus userFeedback when the user typed a reason;
  - a resumed session copies earlier records into a new file under the same
    uuid, so records are de-duplicated by uuid across files;
  - a subagent's transcript is <session>/subagents/agent-<id>.jsonl;
  - a headless run carries entrypoint=sdk-cli.

Usage: extract.py [--days N] [--out PATH] [--projects-dir DIR]
"""
import argparse
import collections
import datetime as dt
import json
import os
import re
import sys
import time

MAX_DAYS = 30
MIN_SIGNALS = 5
LIVE_SECS = 600
CAPS = {"corrections": 40, "interrupts": 25, "rejections": 25, "errors": 25, "retries": 20}
MAX_BYTES = 60000
USER_CHARS, ASSIST_CHARS, ERR_CHARS, CMD_CHARS = 400, 300, 240, 160
CLAUDE_DIR = os.path.expanduser(os.environ.get("CLAUDE_CONFIG_DIR", "~/.claude"))
AGENTS_MD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "AGENTS.md")

EXTRA_PATTERNS = [
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?(?:-----END [A-Z ]*PRIVATE KEY-----|$)", "<private-key>"),
    (r"gh[pousr]_[A-Za-z0-9]{20,}", "[REDACTED]"),
    (r"github_pat_[A-Za-z0-9_]{20,}", "[REDACTED]"),
    (r"xox[abposr]-[A-Za-z0-9-]{10,}", "[REDACTED]"),
    (r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{5,}", "<jwt>"),
    (r"(?i)\b((?:password|passwd|pwd|secret|token|api[_-]?key|client[_-]?secret|access[_-]?key|auth)"
     r"[\"']?\s*[:=]\s*[\"']?)[^\s\"'&,;]{4,}", r"\1[REDACTED]"),
    (r"(?i)([?&](?:code|token|access_token|refresh_token|key|secret|sig|signature|state)=)[^&\s\"']+", r"\1[REDACTED]"),
    (r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "<email>"),
    (r"(?<![A-Za-z0-9+=_-])(?=[A-Za-z0-9+=_-]*\d)(?=[A-Za-z0-9+=_-]*[a-z])(?=[A-Za-z0-9+=_-]*[A-Z])"
     r"[A-Za-z0-9+=_-]{40,}", "<opaque>"),
]


def load_canonical():
    pats = []
    try:
        with open(AGENTS_MD, encoding="utf-8") as fh:
            para = fh.read().split("add new patterns here only", 1)[1].split("\n\n", 1)[0]
        for tok in re.findall(r"`([^`]+)`", para):
            if re.search(r"[\\\[{(+*?]", tok):
                pats.append(re.compile(tok).pattern)
    except (OSError, IndexError, re.error):
        pass
    if not pats:
        sys.exit("retro: redaction list not found in AGENTS.md (section \"Never store\"); refusing to write a digest")
    return pats


REDACTORS = []


def redact(s):
    for rx, repl in REDACTORS:
        s = rx.sub(repl, s)
    return s


def clip(s, n, tail=False):
    s = redact(re.sub(r"\s+", " ", s or "").strip())
    if len(s) <= n:
        return s
    return "…" + s[-n:] if tail else s[:n] + "…"


STRONG = [re.compile(p, re.I) for p in (
    r"\bwhy (did|would|are|were|have|has|do) you\b",
    r"\byou (didn'?t|did not|missed|forgot|ignored|skipped|broke|keep|still|always|never(?! know))\b",
    r"(?<!what )(?<!everything )(?<!anything )(?<!things )\bi (said|told you|asked you|already (said|told|asked)|meant)\b",
    r"\bthat'?s (wrong|not (right|true|accurate|what|it))\b",
    r"\bnot what i\b",
    r"\b(you'?re|you are|that'?s|that is|it'?s|it is|this is|thats|its) (just |plain |completely |still |all )*(wrong|incorrect|inaccurate|not accurate)\b",
    r"^(no+[,.!\s]+)?(wrong|incorrect)\b",
    r"\bwhat are you on about\b",
    r"\bmakes no sense\b",
    r"\bdone it wrong\b",
    r"\bi didn'?t ask\b",
    r"\b(undo|revert) (that|this|it)\b",
    r"(^|[.!]\s+|please |just )stop (doing|polling|that|it)\b",
    r"\bwhy (say|would you say|is it saying)\b",
)]
OPENER = re.compile(r"^(no+|nope|nah|actually|wait|don'?t|stop(?! at))\b", re.I)
OFFER = re.compile(r"\?|\b(should i|shall i|do you want|want me to|i can|decision|option|or leave)\b", re.I)
BENIGN = re.compile(r"^(no+|nah|nope)[,.!\s]*((no|it'?s|its|that'?s|thats)\s+)*"
                    r"(fine|ok|okay|good|worries|n\s?eed|done|thanks|all|it|just|problem|what)\b"
                    r"|^(no+|nah|nope)[.!\s]*$"
                    r"|^((no+|nah|nope)[,.!\s]+)?don'?t worry\b", re.I)
TIMING = re.compile(r"^(ok(ay)?|yes|yeah|yep|approved?|continue|go( on| ahead)?|proceed|retry|"
                    r"try (it )?(now|again)|done|logged in|(it'?s|its) (open|done|there))\b", re.I)
INTERRUPT_RE = re.compile(r"^\[Request interrupted by user")
IMAGE_TAG = re.compile(r"^(\[Image #\d+\]\s*)+")


def correction_score(text, prev_assistant):
    head = text[:300]
    score = 2 * min(2, sum(1 for rx in STRONG if rx.search(head)))
    if OPENER.search(head):
        score += 0 if OFFER.search(prev_assistant[-800:]) else 1
    if BENIGN.search(head):
        score -= 2
    if not prev_assistant.strip():
        score -= 1
    return score


def user_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(b.get("text", "") for b in content
                        if isinstance(b, dict) and b.get("type") == "text")
    return ""


def is_human_prompt(d, text):
    if d.get("isMeta") or d.get("isSidechain"):
        return False
    if (d.get("origin") or {}).get("kind") not in ("human", None):
        return False
    if d.get("promptSource") in ("sdk", "system"):
        return False
    t = text.lstrip()
    return bool(t) and not t.startswith(("<", "[Request interrupted", "[Image: "))


SUBCMD = re.compile(r"^[a-z][a-z0-9:_-]{1,30}$")
INTERP = {"python", "python3", "bash", "sh", "zsh", "node"}
SKIP_PROGS = {"cd", "export", "source", ".", "set", "true", "sleep"}
GENERIC = {"grep", "rg", "cat", "sed", "awk", "ls", "for", "while", "if", "mkdir", "wc", "head",
           "tail", "echo", "printf", "find", "cut", "sort", "uniq", "tr", "diff", "rm", "cp", "mv",
           "test", "[", "jq", "xargs", "touch", "chmod", "pwd", "which", "date", "open", "pbcopy",
           "python3 <inline>", "python <inline>", "bash <inline>", "node <inline>",
           "git status", "git add", "git commit", "git log", "git diff", "git show", "git fetch",
           "git checkout", "git switch", "git pull", "git push", "git branch", "git rev-parse",
           "git stash", "git worktree", "git remote", "git merge", "git rebase", "git reset"}


def is_specific(sh):
    return bool(sh) and sh not in GENERIC and sh.split(" ", 1)[0] not in GENERIC


def shape(cmd):
    first = (cmd or "").strip().split("\n", 1)[0]
    for seg in re.split(r"\s*(?:&&|\|\||;|\|)\s*", first):
        toks = seg.split()
        if toks and re.match(r"^[\w-]+\(\)\{?$", toks[0]):
            toks = toks[1:]
            if toks and toks[0] == "{":
                toks = toks[1:]
        while toks and (re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", toks[0]) or toks[0] in ("sudo", "time", "command", "env")):
            toks = toks[1:]
        if not toks or toks[0] in SKIP_PROGS:
            continue
        prog = os.path.basename(toks[0])
        rest = toks[1:]
        if prog == "git" and len(rest) >= 2 and rest[0] == "-C":
            rest = rest[2:]
        if prog in INTERP and rest:
            nxt = rest[0]
            if nxt in ("-", "-c") or nxt.startswith("<<"):
                return f"{prog} <inline>"
            if nxt == "-m" and len(rest) > 1:
                return f"{prog} -m {rest[1]}"
            if not nxt.startswith("-"):
                return f"{prog} {os.path.basename(nxt)}"
        words = [prog]
        for t in rest:
            if len(words) == 3 or not SUBCMD.match(t):
                break
            words.append(t)
        return " ".join(words)
    return ""


ERRORISH = re.compile(r"error|fatal|traceback|exception|not found|denied|no such|invalid|failed|"
                      r"cannot|can't|refus|usage:|unknown|blocked|timed out|permission", re.I)
ZERO_COUNT = re.compile(r"\b0 (?:failed|failures?|errors?)\b", re.I)


def errorish(s):
    return ERRORISH.search(ZERO_COUNT.sub("", s))


def is_real_error(name, text):
    if name != "Bash":
        return True
    lines = [ln for ln in re.sub(r"^Exit code \d+\s*", "", text or "").splitlines() if ln.strip()]
    return bool(errorish("\n".join(lines[:3] + lines[-3:])[:1200]))


def err_line(text):
    lines = [ln.strip() for ln in (text or "").splitlines() if ln.strip()]
    lines = [ln for ln in lines if not re.match(r"^Exit code \d+$", ln)] or lines or [""]
    for ln in reversed(lines[-3:]):
        if errorish(ln):
            return ln
    for ln in lines[:3]:
        if errorish(ln):
            return ln
    return lines[0]


def norm_error(text):
    key = err_line(text)
    key = re.sub(r"(/[\w.@+-]+)+", "<path>", key)
    key = re.sub(r"([=*#~_-])\1+", r"\1\1", key)
    key = re.sub(r"\d+", "#", key)
    key = re.sub(r"(['\"]).*?\1", "'…'", key)
    return redact(key[:120])


def tool_summary(name, inp):
    if not isinstance(inp, dict):
        return name
    if name == "Bash":
        return f"Bash `{inp.get('command', '')}`"
    for k in ("file_path", "path", "pattern", "skill", "url", "query", "description", "prompt"):
        if k in inp:
            return f"{name} {k}={inp[k]}"
    return f"{name} {json.dumps(inp)[:200]}"


def result_text(block):
    c = block.get("content")
    if isinstance(c, list):
        c = " ".join(x.get("text", "") for x in c if isinstance(x, dict))
    return c if isinstance(c, str) else json.dumps(c)


def iter_files(root, since):
    try:
        projects = list(os.scandir(root))
    except OSError:
        return
    now = time.time()

    def mtime(e):
        try:
            return e.stat().st_mtime
        except OSError:
            return 0
    for proj in projects:
        if not proj.is_dir():
            continue
        try:
            entries = list(os.scandir(proj.path))
        except OSError:
            continue
        for ent in entries:
            if ent.is_file() and ent.name.endswith(".jsonl"):
                if mtime(ent) >= since:
                    yield ent.path, proj.name, False
            elif ent.is_dir():
                try:
                    subs = list(os.scandir(os.path.join(ent.path, "subagents")))
                except OSError:
                    continue
                for s in subs:
                    if s.name.endswith(".jsonl") and since <= mtime(s) <= now - LIVE_SECS:
                        yield s.path, proj.name, True


def project_name(cwd, fallback):
    if not cwd:
        return fallback
    if "/.claude/worktrees/" in cwd:
        repo, name = cwd.split("/.claude/worktrees/", 1)
        if repo != os.path.expanduser("~"):
            return os.path.basename(repo)
        return name.split("/", 1)[0]
    return os.path.basename(cwd.rstrip("/")) or fallback


class Extractor:
    def __init__(self, since):
        self.since_iso = dt.datetime.fromtimestamp(since, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
        self.seen = set()
        self.files = 0
        self.subagent_files = 0
        self.sessions = set()
        self.projects = collections.Counter()
        self.prompts = 0
        self.corrections = []
        self.interrupts = []
        self.rejections = []
        self.errors = {}
        self.retries = {}

    def scan(self, path, proj_dir, subagent):
        sid = os.path.basename(path).removesuffix(".jsonl")
        parent = os.path.basename(os.path.dirname(os.path.dirname(path)))[:8]
        session = parent if subagent else sid[:8]
        project = proj_dir
        last_assist = ""
        tools = {}
        bash_hist = []
        awaiting = []
        counted = False
        try:
            fh = open(path, encoding="utf-8", errors="replace")
        except OSError:
            return
        self.files += 1
        self.subagent_files += subagent
        with fh:
            for line in fh:
                if line.startswith(('{"type":"file-history', '{"type":"attachment"')):
                    continue
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                if not isinstance(d, dict):
                    continue
                if d.get("entrypoint") == "sdk-cli":
                    return
                if d.get("cwd") and project == proj_dir:
                    project = project_name(d["cwd"], proj_dir)
                t = d.get("type")
                if t not in ("user", "assistant"):
                    continue
                ts = d.get("timestamp") or ""
                uid = d.get("uuid")
                live = ts[:19] >= self.since_iso and uid not in self.seen
                if uid:
                    self.seen.add(uid)
                if live and not counted and not subagent:
                    self.sessions.add(sid)
                    self.projects[project] += 1
                    counted = True
                where = {"project": project, "session": session, "ts": ts[:16]}
                content = (d.get("message") or {}).get("content")

                if t == "assistant":
                    for b in content if isinstance(content, list) else []:
                        if not isinstance(b, dict):
                            continue
                        if b.get("type") == "text" and b.get("text", "").strip():
                            last_assist = b["text"]
                        elif b.get("type") == "tool_use":
                            name, inp = b.get("name", ""), b.get("input") or {}
                            tools[b.get("id")] = (name, inp)
                            last_assist = last_assist[-200:] + " → " + tool_summary(name, inp)
                    if len(tools) > 200:
                        for k in list(tools)[:100]:
                            tools.pop(k, None)
                    continue

                if isinstance(content, list) and any(isinstance(b, dict) and b.get("type") == "tool_result" for b in content):
                    for b in content:
                        if not isinstance(b, dict) or b.get("type") != "tool_result":
                            continue
                        name, inp = tools.pop(b.get("tool_use_id"), ("?", {}))
                        if live:
                            self._tool_result(d, b, name, inp, where, bash_hist, awaiting, subagent)
                    continue

                text = user_text(content)
                if not live or subagent:
                    continue
                if INTERRUPT_RE.match(text.strip()):
                    sig = dict(where, kind="interrupt", before=clip(last_assist, ASSIST_CHARS, tail=True), next="")
                    self.interrupts.append(sig)
                    awaiting.append(sig)
                    continue
                if not is_human_prompt(d, text):
                    continue
                text = IMAGE_TAG.sub("", text.strip())
                self.prompts += 1
                score = correction_score(text, last_assist)
                for sig in awaiting:
                    sig["next"] = clip(text, USER_CHARS)
                    sig["next_score"] = score
                if score >= 1 and not awaiting:
                    self.corrections.append(dict(where, score=score, user=clip(text, USER_CHARS),
                                                 before=clip(last_assist, ASSIST_CHARS, tail=True)))
                awaiting = []
                last_assist = ""

    def _tool_result(self, d, b, name, inp, where, bash_hist, awaiting, subagent):
        kind = d.get("toolDenialKind")
        text = result_text(b)
        if kind == "user-rejected" or (kind and kind != "interrupted" and "denied" in text.lower()) or kind == "automode-blocked":
            if subagent:
                return
            sig = dict(where, kind=kind or "denied", tool=clip(tool_summary(name, inp), CMD_CHARS),
                       feedback=clip(d.get("userFeedback") or "", USER_CHARS), next="")
            self.rejections.append(sig)
            if not sig["feedback"]:
                awaiting.append(sig)
            return
        if kind == "interrupted":
            return
        failed = bool(b.get("is_error")) and is_real_error(name, text)
        if name == "Bash":
            cmd = (inp or {}).get("command", "")
            sh = shape(cmd)
            for prev in reversed(bash_hist[-3:]):
                if prev[1] and prev[0] == sh and is_specific(sh):
                    r = self.retries.setdefault(sh, {"count": 0, "fixed": 0, "sessions": set(), "example": None})
                    r["count"] += 1
                    r["fixed"] += 0 if failed else 1
                    r["sessions"].add(where["session"])
                    if r["example"] is None or (not failed and not r["example"]["fixed"]):
                        r["example"] = dict(where, failed_cmd=clip(prev[2], CMD_CHARS), error=clip(err_line(prev[3]), ERR_CHARS),
                                            retry_cmd=clip(cmd, CMD_CHARS), fixed=not failed)
                    break
            bash_hist.append((sh, failed, cmd, text if failed else ""))
            del bash_hist[:-6]
        if not failed:
            return
        key = (name, norm_error(text))
        e = self.errors.setdefault(key, {"count": 0, "sessions": set(), "projects": set(), "example": None})
        e["count"] += 1
        e["sessions"].add(where["session"])
        e["projects"].add(where["project"])
        if e["example"] is None:
            e["example"] = dict(where, call=clip(tool_summary(name, inp), CMD_CHARS),
                                error=clip(err_line(text), ERR_CHARS))


def lesson_interrupt(s):
    return s.get("next_score", 0) >= 1 or len(s["next"]) >= 80


def says_why(s):
    t = s["feedback"] or s["next"]
    return bool(t) and (not TIMING.search(t) or any(rx.search(t[:300]) for rx in STRONG))


def render(x, since, now, days):
    sec = collections.OrderedDict()

    seen_txt = set()
    items = []
    ranked = sorted(x.corrections, key=lambda c: c["ts"], reverse=True)
    for c in sorted(ranked, key=lambda c: -c["score"]):
        k = c["user"][:80].lower()
        if k in seen_txt:
            continue
        seen_txt.add(k)
        items.append(f"- [{c['project']} {c['session']} {c['ts']}] score {c['score']}\n"
                     f"  assistant: {c['before']}\n  user: {c['user']}")
    sec["corrections"] = (len(x.corrections), items)

    ints = [s for s in x.interrupts if lesson_interrupt(s)]
    ints = sorted(sorted(ints, key=lambda s: s["ts"], reverse=True), key=lambda s: -s.get("next_score", -9))
    sec["interrupts"] = (len(ints), [
        f"- [{s['project']} {s['session']} {s['ts']}]\n  assistant was: {s['before']}\n  user next: {s['next'] or '(nothing)'}"
        for s in ints])

    rej = sorted([s for s in x.rejections if says_why(s)], key=lambda s: s["ts"], reverse=True)
    sec["rejections"] = (len(rej), [
        f"- [{s['project']} {s['session']} {s['ts']}] {s['kind']}: {s['tool']}\n"
        f"  user said: {s['feedback'] or s['next'] or '(nothing)'}" for s in rej])

    errs = sorted(x.errors.items(), key=lambda kv: (-len(kv[1]["sessions"]), -kv[1]["count"]))
    sec["errors"] = (sum(e["count"] for e in x.errors.values()), [
        f"- {e['count']}x in {len(e['sessions'])} session(s), {', '.join(sorted(e['projects'])[:3])} — {name}: {key}\n"
        f"  e.g. [{e['example']['session']} {e['example']['ts']}] {e['example']['call']}\n  error: {e['example']['error']}"
        for (name, key), e in errs])

    rets = sorted(x.retries.items(), key=lambda kv: (-len(kv[1]["sessions"]), -kv[1]["count"]))
    sec["retries"] = (sum(r["count"] for r in x.retries.values()), [
        f"- `{sh}` failed then re-run {r['count']}x in {len(r['sessions'])} session(s), {r['fixed']} fixed on retry\n"
        f"  e.g. [{r['example']['project']} {r['example']['session']}] failed: {r['example']['failed_cmd']}\n"
        f"  error: {r['example']['error']}\n  retry: {r['example']['retry_cmd']}"
        for sh, r in rets])

    signals = sum(sec[k][0] for k in ("corrections", "interrupts", "rejections", "retries"))
    out = [
        "# Transcript retro digest",
        "",
        f"Window: {dt.datetime.fromtimestamp(since).strftime('%Y-%m-%d %H:%M')} to "
        f"{dt.datetime.fromtimestamp(now).strftime('%Y-%m-%d %H:%M')} local ({days} days). "
        f"{x.files} transcript files ({x.subagent_files} subagent), {len(x.sessions)} sessions, {x.prompts} typed prompts.",
        "Sessions by project: " + (", ".join(f"{p} {n}" for p, n in x.projects.most_common(12)) or "(none)"),
        "",
    ]
    if signals < MIN_SIGNALS:
        out += [f"Too few signals: {signals} corrections, interrupts, rejections and retries "
                f"(fewer than {MIN_SIGNALS}). Widen --days or skip this retro.", ""]
    out += [
        "Excerpts are redacted and trimmed. Corrections are a KEYWORD HEURISTIC: read the",
        "assistant turn before each one and discard replies that are not pushback.",
        "Interrupts and rejections show what the user typed next, which is usually the reason.",
        "Format: [project session-id timestamp].",
    ]
    titles = {
        "corrections": "User corrections / pushback",
        "interrupts": "User interrupts",
        "rejections": "Rejected or denied tool calls (silent and \"try now\"-type ones excluded)",
        "errors": "Tool errors (grouped by error shape; non-zero exits with no error text excluded)",
        "retries": "Same command failed, then re-run",
    }
    kept = {k: v[1][:CAPS[k]] for k, v in sec.items()}
    fixed = sum(len(ln.encode()) + 1 for ln in out) + 120 * len(titles)

    def size():
        return sum(len(i.encode()) + 1 for v in kept.values() for i in v)
    while size() > MAX_BYTES - fixed and any(kept.values()):
        big = max(kept, key=lambda k: sum(len(i.encode()) for i in kept[k]))
        kept[big].pop()
    for k, title in titles.items():
        out += ["", f"## {title} — {len(kept[k])} shown of {sec[k][0]} found", ""]
        out += kept[k] or ["(none)"]
    text = "\n".join(out) + "\n"
    stats = {k: [sec[k][0], len(kept[k])] for k in sec}
    stats["signals"] = signals
    return text, stats


def main():
    ap = argparse.ArgumentParser(description="Mine Claude Code transcripts into a retro digest.")
    ap.add_argument("--days", type=int, default=7, help=f"window in days (clamped to 1..{MAX_DAYS})")
    ap.add_argument("--out", help="digest path (default: stdout); keep it out of the vault tree")
    ap.add_argument("--projects-dir", default=os.path.join(CLAUDE_DIR, "projects"))
    a = ap.parse_args()
    days = max(1, min(MAX_DAYS, a.days))
    REDACTORS[:] = [(re.compile(p), "[REDACTED]") for p in load_canonical()]
    REDACTORS.extend((re.compile(p), r) for p, r in EXTRA_PATTERNS)

    now = time.time()
    since = now - days * 86400
    x = Extractor(since)
    for path, proj, sub in iter_files(a.projects_dir, since):
        x.scan(path, proj, sub)
    text, stats = render(x, since, now, days)
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        fd = os.open(a.out, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
    else:
        sys.stdout.write(text)
    stats.update(days=days, files=x.files, sessions=len(x.sessions), prompts=x.prompts,
                 bytes=len(text.encode()), seconds=round(time.time() - now, 1))
    print(json.dumps(stats), file=sys.stderr)


if __name__ == "__main__":
    main()
