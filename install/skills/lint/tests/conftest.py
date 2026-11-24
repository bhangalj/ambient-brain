import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "lint.py"


def write(root: Path, rel: str, text: str) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def ago(days: int) -> str:
    return (date.today() - timedelta(days=days)).isoformat()


def tasks(now=None, next_=None, blocked=None, later=None, personal=None, head="") -> str:
    def block(name, items):
        return f"## {name}\n" + "".join(f"{i}\n" for i in items) + "\n"
    return ("---\ntype: tasks\nupdated: 2026-01-01\n---\n# Tasks\n\n> Header prose.\n" + head + "\n"
            + block("Now", now if now is not None else [f"- Ship it — [[topics/alpha]] ({ago(1)})"])
            + block("Next", next_ if next_ is not None else [f"- Plan it ({ago(3)})"])
            + block("Blocked", blocked if blocked is not None else [f"- Wait (waiting on [[people/jane-doe|Jane]]) ({ago(2)})"])
            + block("Later", later if later is not None else [f"- Someday ({ago(5)})"])
            + block("Personal", personal if personal is not None else [f"- Dentist ({ago(60)})"]))


@pytest.fixture
def vault(tmp_path: Path) -> Path:
    write(tmp_path, "index.md", "---\ntype: meta\nupdated: 2026-01-01\n---\n# Index\n\n"
          "> A long header line that runs well past the eighty character cap but is not an entry.\n\n"
          "- [[tasks]] — my open items\n"
          "- [[people/_index]] — colleagues, one line each (sharded)\n"
          "- [[projects/acme/_project|Acme]] — the acme project\n"
          "- [[topics/alpha]] — alpha topic\n"
          "- [[meetings/2026-01-01-kickoff]] — kickoff meeting\n")
    write(tmp_path, "people/_index.md", "---\ntype: meta\nupdated: 2026-01-01\n---\n- [[people/jane-doe]] — Jane\n")
    write(tmp_path, "people/jane-doe.md", "---\ntype: person\nname: Jane Doe\nupdated: 2026-01-01\n---\n# Jane\n")
    write(tmp_path, "projects/acme/_project.md", "---\ntype: project\nname: Acme\nstatus: active\nupdated: 2026-01-01\n---\n"
          "See [[projects/acme/plan|plan]] and [[people/jane-doe#Role]].\n")
    write(tmp_path, "projects/acme/plan.md", "---\ntype: project-doc\nproject: \"[[projects/acme/_project]]\"\nupdated: 2026-01-01\n---\n"
          "| who | link |\n|---|---|\n| Jane | [[people/jane-doe\\|Jane]] |\n")
    write(tmp_path, "topics/alpha.md", "---\ntype: topic\nupdated: 2026-01-01\n---\nAlpha. Example: `[[people/<slug>]]`\n"
          "<!-- - [[topics/<slug>]] -->\n```\n[[nowhere/at-all]]\n```\n")
    write(tmp_path, "meetings/2026-01-01-kickoff.md", "---\ntype: meeting\ndate: 2026-01-01\nupdated: 2026-01-01\n"
          "source: \"[[../sources/2026-01-01-kickoff]]\"\n---\nKickoff with [[people/jane-doe|Jane]].\n")
    write(tmp_path, "sources/2026-01-01-kickoff.md", "raw transcript\n")
    write(tmp_path, "tasks.md", tasks())
    return tmp_path


@pytest.fixture
def lint():
    def run(root: Path) -> tuple[int, list[list[str]]]:
        r = subprocess.run([sys.executable, "-I", str(SCRIPT), "--vault", str(root)], capture_output=True, text=True)
        assert r.stderr == ""
        return r.returncode, [line.split("\t") for line in r.stdout.splitlines()]
    return run


def checks(rows: list[list[str]]) -> list[str]:
    return [r[0] for r in rows]
