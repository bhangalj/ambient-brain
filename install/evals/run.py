#!/usr/bin/env python3
"""Model-agnostic eval runner for the brain skills (remember, recall, lint).

Stdlib only. Nothing here knows which model or harness is under test: the agent
is any shell command that reads a prompt on stdin and prints its final answer on
stdout. Each case runs against a throwaway copy of `fixture/`, made a git repo
with a local bare `origin`, so a skill can commit and push without touching the
real vault. Grading is deterministic: each case's `check.py` inspects the vault
files, the git state and the agent's stdout. No LLM judge.

Layout:
  fixture/                      the test vault (AGENTS.md is copied in from the
                                repo root at run time, so it never drifts)
  cases/<skill>/<case>/
    prompt.md                   the user's request, verbatim
    setup.py   (optional)       mutates the fresh vault before the agent runs
    check.py                    exits 0 on pass; prints one line per failure
  evalkit.py                    helpers that check.py imports

Usage:
  ./run.py --agent 'costed.py claude --dangerously-skip-permissions'
  ./run.py --agent '<any CLI agent>' --skill recall --runs 3
  ./run.py --agent 'true'       # no-op agent: proves the checks can fail

The agent may write its cost in USD (one float) to the file named in $EVAL_COST_FILE.
costed.py (on the agent's PATH) does this for claude. A run without it prints `cost ?`.
"""
import argparse
import fnmatch
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))

PROMPT = """Read the skill file {skill}/SKILL.md and follow it exactly to handle the request at the end.

The vault for this task is {vault}. Use ONLY this vault. Ignore any other vault path
you may be configured with (for example ~/brain or __VAULT_DIR__): every reference to
the vault in the skill means {vault}. Its git remote `origin` is a local test remote,
so pushing to it is safe.

This run is non-interactive and nobody can answer questions. Where the skill says to
wait for the user's OK, stop at that point and report instead.

Request:
{prompt}"""


def git(cwd, *args):
    return subprocess.run(["git", "-C", cwd, *args], capture_output=True,
                          text=True).stdout.strip()


def real_vault_state(path):
    if not os.path.isdir(os.path.join(path, ".git")):
        return None
    return git(path, "rev-parse", "HEAD"), git(path, "status", "--porcelain")


def build_vault(root, repo, skill, case_dir):
    vault = os.path.join(root, "vault")
    shutil.copytree(os.path.join(HERE, "fixture"), vault)
    shutil.copy(os.path.join(repo, "AGENTS.md"), os.path.join(vault, "AGENTS.md"))
    shutil.copytree(os.path.join(repo, "install", "skills", skill), os.path.join(root, "skill"))
    remote = os.path.join(root, "remote.git")
    q = dict(capture_output=True, check=True)
    subprocess.run(["git", "init", "-q", "-b", "main", vault], **q)
    for k, v in (("user.name", "Eval"), ("user.email", "eval@example.invalid"),
                 ("commit.gpgsign", "false")):
        subprocess.run(["git", "-C", vault, "config", k, v], **q)
    subprocess.run(["git", "-C", vault, "add", "-A"], **q)
    subprocess.run(["git", "-C", vault, "commit", "-q", "-m", "fixture"], **q)
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", remote], **q)
    subprocess.run(["git", "-C", vault, "remote", "add", "origin", remote], **q)
    subprocess.run(["git", "-C", vault, "push", "-q", "-u", "origin", "main"], **q)
    setup = os.path.join(case_dir, "setup.py")
    if os.path.exists(setup):
        subprocess.run([sys.executable, setup], cwd=vault, check=True)
    return vault, remote


def run_case(args, skill, case_dir):
    root = tempfile.mkdtemp(prefix=f"brain-eval-{skill}-")
    vault, remote = build_vault(root, args.root, skill, case_dir)
    base_head = git(vault, "rev-parse", "HEAD")
    base_status = git(vault, "status", "--porcelain")
    with open(os.path.join(case_dir, "prompt.md"), encoding="utf-8") as f:
        prompt = PROMPT.format(skill=os.path.join(root, "skill"), vault=vault,
                               prompt=f.read().strip())
    out_path = os.path.join(root, "agent-stdout.txt")
    cost_path = os.path.join(root, "agent-cost.txt")
    started = time.time()
    p = subprocess.Popen(args.agent, shell=True, cwd=root, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                         start_new_session=True,
                         env=dict(os.environ, EVAL_COST_FILE=cost_path,
                                  PATH=HERE + os.pathsep + os.environ["PATH"]))
    try:
        stdout, stderr = p.communicate(prompt, timeout=args.timeout)
        rc = p.returncode
        if stderr.strip():
            with open(os.path.join(root, "agent-stderr.txt"), "w") as f:
                f.write(stderr)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        stdout = p.communicate()[0]
        rc = "timeout"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(stdout)
    try:
        with open(cost_path, encoding="utf-8") as f:
            cost = float(f.read())
    except (OSError, ValueError):
        cost = None
    env = dict(os.environ, VAULT=vault, REMOTE=remote, OUT=out_path,
               BASE_HEAD=base_head, BASE_STATUS=base_status,
               PYTHONPATH=HERE)
    c = subprocess.run([sys.executable, os.path.join(case_dir, "check.py")],
                       env=env, capture_output=True, text=True)
    failures = (c.stdout + c.stderr).strip()
    if rc != 0:
        failures = f"agent exit {rc}\n{failures}".strip()
    passed = c.returncode == 0 and rc == 0
    if not args.keep and passed:
        shutil.rmtree(root, ignore_errors=True)
    return passed, failures, root, time.time() - started, cost


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--agent", required=True,
                    help="shell command; prompt on stdin, final answer on stdout")
    ap.add_argument("--root", default=REPO,
                    help="checkout whose skills and AGENTS.md are under test (default: this one)")
    ap.add_argument("--skill", action="append",
                    help="limit to a skill (repeatable); default: all")
    ap.add_argument("--case", default="*", help="glob on case name")
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--timeout", type=int, default=900, help="seconds per run")
    ap.add_argument("--keep", action="store_true",
                    help="keep temp dirs of passing runs too (failing ones are always kept)")
    ap.add_argument("--real-vault", default=REPO,
                    help="vault that must stay untouched; warn if it changes")
    args = ap.parse_args()

    cases_root = os.path.join(HERE, "cases")
    skills = args.skill or sorted(d for d in os.listdir(cases_root)
                                  if os.path.isdir(os.path.join(cases_root, d)))
    total_fail = 0
    costs = []
    cost_missing = 0
    for skill in skills:
        sdir = os.path.join(cases_root, skill)
        for case in sorted(os.listdir(sdir)):
            if not fnmatch.fnmatch(case, args.case):
                continue
            ok = 0
            for i in range(args.runs):
                before = real_vault_state(args.real_vault)
                passed, failures, root, secs, cost = run_case(args, skill, os.path.join(sdir, case))
                after = real_vault_state(args.real_vault)
                ok += passed
                if cost is None:
                    cost_missing += 1
                else:
                    costs.append(cost)
                mark = "PASS" if passed else "FAIL"
                print(f"{mark}  {skill}/{case}  run {i + 1}/{args.runs}  {secs:.0f}s  "
                      f"{'cost ?' if cost is None else f'${cost:.4f}'}", flush=True)
                if not passed:
                    for line in failures.splitlines():
                        print(f"        {line}")
                    print(f"        kept: {root}")
                if before != after:
                    print(f"  WARN  {args.real_vault} changed during this run. "
                          "Check it was a parallel session, not the agent.")
            total_fail += args.runs - ok
    print(f"\n{'all passed' if not total_fail else f'{total_fail} run(s) failed'}")
    if costs:
        print(f"cost  total ${sum(costs):.4f}  mean ${sum(costs) / len(costs):.4f} per costed run")
    if cost_missing:
        print(f"  WARN  {cost_missing} run(s) reported no cost "
              "(timed out, or the agent command did not write $EVAL_COST_FILE)")
    sys.exit(1 if total_fail else 0)


if __name__ == "__main__":
    main()
