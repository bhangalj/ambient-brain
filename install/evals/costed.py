#!/usr/bin/env python3
"""Wrap `claude` so an eval run reports its cost.

Usage:
  ./costed.py claude <claude args...>

Reads the prompt on stdin, prints the final answer on stdout, writes the cost in
USD to $EVAL_COST_FILE when it is set, and exits with the agent's exit code.
"""
import json
import os
import subprocess
import sys


def run_claude(args):
    p = subprocess.run(["claude", "-p", "--output-format", "json", *args],
                       stdin=sys.stdin, capture_output=True, text=True)
    try:
        result = json.loads(p.stdout)
    except ValueError:
        return p, p.stdout, None
    return p, result.get("result", ""), result.get("total_cost_usd")


def main():
    if len(sys.argv) < 2 or sys.argv[1] != "claude":
        sys.exit("usage: costed.py claude <agent args...>")
    p, answer, cost = run_claude(sys.argv[2:])
    sys.stderr.write(p.stderr)
    sys.stdout.write(answer)
    path = os.environ.get("EVAL_COST_FILE")
    if path and cost is not None:
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"{cost}\n")
    sys.exit(p.returncode)


if __name__ == "__main__":
    main()
