import collections
import re


SEVERITIES = tuple((name, re.compile(rf"({rx})(\s+(findings?|issues?))?(\s*\(\d+\))?", re.I)) for name, rx in (
    ("Blocking", r"blocking|major|critical|high"),
    ("Should-fix", r"should([- ]fix)?|judge?ment( calls?)?|non[- ]blocking|medium"),
    ("Nit", r"nits?|minor|suggestions?|low")))
SEV_WORD = r"blocking|major|critical|high|should(?:[- ]fix)?|judge?ment(?: calls?)?|non[- ]blocking|medium|nits?|minor|low"
REVIEW_HEADING = re.compile(r"^(?:#+\s*(.*)|\*\*([^*]+)\*\*\s*(?:\(\d+\))?:?)$")
REVIEW_ITEM = re.compile(r"^(?:[-*]|\d+[.)])\s+(.*)")
REVIEW_OWN_SEV = re.compile(rf"^(?:\*\*|\[)?({SEV_WORD})\b(?:\*\*|\])?\s*(?:·|:|—|/|,|-\s)|·\s*({SEV_WORD})\s*[·(]", re.I)
REVIEW_BARE_SEV = re.compile(rf"·\s*({SEV_WORD})\s*[·(]", re.I)
REVIEW_NOT_A_FINDING = re.compile(rf"^\W*(({SEV_WORD})\W*:?\s*\d+\b|(none|nothing|no (findings?|issues?))\W*$)", re.I)
REVIEW_BUCKETS = tuple((name, re.compile(rx, re.I)) for name, rx in (
    ("stale docs", r"\bstale\b|out of date|outdated|no longer (true|accurate|matches|exists?)"
                   r"|still (says|describes|claims|documents|names|lists|refers)|\bdocs? (drift|still)\b|not updated"),
    ("one-caller helper or duplication", r"\b(one|single|only one) (caller|callsite|call site)\b|used (only )?once"
                                         r"|duplicat|copy-?past|copied from|same (logic|code|check)|pass-through"),
    ("silent fallback", r"silent|fall(s|ing)? ?back|fallback|swallow|\bdefaults? (to|hides?|masks?)\b"
                        r"|hides? (the |a )?(missing|error|failure|bad)|except:\s*pass|broad except"),
    ("missing test", r"\bno (test|regression test|coverage)\b|untested|not tested|missing (a )?tests?"
                     r"|without (a )?tests?\b|lacks? (a )?tests?|has no tests?"),
    ("test cannot fail", r"can ?n[o']t fail|never fails?|(passes|would pass) (even )?without|vacuous|tautolog"
                         r"|proves nothing|always pass"),
    ("concurrency or race", r"\brace\b|concurren|(?<![.\w-])lock(s|ing|ed)?\b|atomic|toctou|in parallel|simultaneous"),
    ("unproven against the live system", r"\blive (system|org|data|run|record|graph)|real (org|system|path|record|data|query)"
                                         r"|against prod|unverified|not verified|never (ran|run|exercised|tested) against"
                                         r"|only (in )?(a )?(mock|stub|simulat)"),
    ("limits", r"governor|\b(request|payload|body|response|message|batch) (size|too large)|\bHTTP 413\b"
               r"|paginat|\bpag(ing|ed)\b|next ?page|page size|truncat"),
))


def severity(word):
    return next((name for name, rx in SEVERITIES if rx.fullmatch(word.strip(" *#:"))), None)


def review_findings(text):
    """[severity, first line, body] per finding in a reviewer's reply."""
    found, sev, cur = [], None, None
    for line in text.splitlines():
        if line[:1].isspace():
            if cur and line.strip():
                cur[2] += "\n" + line.strip()
            continue
        cur = None
        heading = REVIEW_HEADING.match(line.strip())
        if heading:
            sev = severity(heading.group(1) or heading.group(2))
            continue
        item = REVIEW_ITEM.match(line)
        if not item and line.strip():
            sev = None
        body = item.group(1) if item else line
        own = (REVIEW_OWN_SEV if item else REVIEW_BARE_SEV).search(body)
        s = severity(next(g for g in own.groups() if g)) if own else sev if item else None
        if s and not REVIEW_NOT_A_FINDING.match(body):
            cur = [s, body, body]
            found.append(cur)
    return found


def render(runs, reviews, builds, in_run):
    loop_items, blocking = [], []
    buckets = {name: [0, set()] for name, _ in REVIEW_BUCKETS}
    for r in runs:
        revs = in_run(r, reviews)
        if not revs:
            continue
        run_builds = in_run(r, builds)
        first = next((b for b in run_builds if b["ts"] < revs[0]["ts"]), None)
        rounds, i, prev_ts = [], 0, None
        for v in revs:
            if prev_ts is None or any(prev_ts < b["ts"] < v["ts"] for b in run_builds):
                i += 1
            prev_ts = v["ts"]
            found = review_findings(v["final"])
            c = collections.Counter(f[0] for f in found)
            rounds.append(f"round {i} B{c['Blocking']} S{c['Should-fix']} N{c['Nit']}")
            for sev, first_line, body in found:
                if sev == "Blocking":
                    blocking.append((v["ts"], f"[{r['project']} {r['session']} r{i}]", first_line))
                if sev == "Nit":
                    continue
                for name, rx in REVIEW_BUCKETS:
                    if rx.search(body):
                        buckets[name][0] += 1
                        buckets[name][1].add(r["session"])
        first_build = f"{first['type']} ({first['model']})" if first else "none"
        loop_items.append(f"- [{r['project']} {r['session']} {r['ts']}] reviews {len(revs)} · first build {first_build} · "
                          + " · ".join(rounds))
    hits = sorted(((name, n, s) for name, (n, s) in buckets.items() if n), key=lambda b: (-len(b[2]), -b[1]))
    loop_items = [f"- repeat: {name} · {n} finding(s) in {len(s)} session(s)" for name, n, s in hits] + loop_items
    return loop_items, sorted(blocking, key=lambda b: b[0], reverse=True)
