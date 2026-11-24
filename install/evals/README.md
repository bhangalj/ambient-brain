# Brain skill evals (`remember`, `recall`, `lint`)

A gate for skill edits. Change a `SKILL.md` (by hand or from a `/retro` proposal),
run this, and keep the edit only when it passes.

**Model-agnostic by rule.** Nothing here is tied to a model or a harness. The agent is
any shell command that reads a prompt on stdin and prints its final answer on stdout.
Grading is deterministic. Each `check.py` reads the vault files, the git state and the
agent's answer. There is no LLM judge and no vendor eval format.

## Run

```bash
./run.py --agent 'costed.py claude --dangerously-skip-permissions --no-session-persistence'
./run.py --agent '<any CLI agent that reads stdin>'
./run.py --agent '<cmd>' --skill lint --case 'tasks-*' --runs 3
./run.py --agent true                                 # no-op agent: every case must FAIL
```

A real agent run spends model credits. `--agent true` spends nothing.

Every run reports its cost in USD, per run and in total. `costed.py` (on the agent's
`PATH`) does this for `claude -p`. A custom agent must write its cost in USD to
`$EVAL_COST_FILE`.

`--no-session-persistence` keeps eval sessions out of the transcripts that `/retro`
mines.

Exit code 0 means all runs passed. A failing run keeps its temp dir and prints the path.
The temp dir holds the vault, `agent-stdout.txt` and `agent-stderr.txt`.

## How a run works

1. Copy `fixture/` to a temp dir. Copy the repo's real `AGENTS.md` into it, so the
   conventions under test never drift from the live ones.
2. Make it a git repo with a local bare `origin`, so commit and push are real.
3. Run the case's `setup.py`, if it has one (for example, plant lint findings or
   leave another session's uncommitted edit).
4. Send the prompt: "read `<skill>/SKILL.md`, use only this vault, the request is …".
5. Run `check.py`. It prints one line per failure.

The runner warns if this checkout changes during a run. Agents that load a global config
(for example `~/.claude/CLAUDE.md`) know the real vault path. The prompt overrides it,
and the warning catches a run that ignores the override.

## Add a case

`cases/<skill>/<case>/prompt.md` holds the user's request, verbatim.
`check.py` starts with `from evalkit import *`, calls `expect(cond, msg)`, and ends with
`done()`. Write the check against a rule the skill states, and make the no-op agent
fail it. If `--agent true` passes a case, the case proves nothing.

The fixture and every case are invented. Keep them that way: no real people, accounts
or meetings.
