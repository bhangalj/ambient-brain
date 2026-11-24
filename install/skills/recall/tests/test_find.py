import os
import subprocess
import sys
from pathlib import Path

import pytest

sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "find.py"


def write(root: Path, rel: str, text: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def find(*args: str, home: Path | None = None) -> str:
    env = {**os.environ, "HOME": str(home)} if home else None
    r = subprocess.run([sys.executable, "-I", str(SCRIPT), *args], capture_output=True, text=True, env=env)
    assert r.returncode == 0 and r.stderr == ""
    return r.stdout


@pytest.fixture
def vault(tmp_path: Path) -> Path:
    write(tmp_path, "projects/acme/_project.md",
          "---\ntype: project\nname: Acme\n---\n# Acme\n\n## State\nAll good.\n\n### Wave B\nWave B ships the Gizmo widget.\n"
          "More text.\n\n## Log\n- 2026-01-01 nothing about it.\n")
    write(tmp_path, "topics/gizmo.md", "---\ntype: topic\n---\n# Gizmo\nGizmo reference.\n")
    write(tmp_path, "topics/noise.md", "---\ntype: topic\n---\n# Noise\n" + "widget widget widget\n" * 5)
    write(tmp_path, "people/jane-doe.md", "---\ntype: person\nname: J. Doe\n---\n# Profile\nWorks on widgets.\n")
    write(tmp_path, "tasks.md", "## Now\n- Ship the Gizmo (2026-01-01)\n")
    write(tmp_path, "sources/raw.md", "Gizmo raw transcript\n")
    write(tmp_path, "install/skills/x.md", "Gizmo in install\n")
    write(tmp_path, "AGENTS.md", "Gizmo in agents\n")
    return tmp_path


def test_section_has_path_heading_chain_and_line_range(vault):
    out = find("wave b", "--vault", str(vault))
    assert "projects/acme/_project.md:10-13" in out
    assert "## State > ### Wave B" in out
    assert "11: Wave B ships the Gizmo widget." in out


def test_case_insensitive_and_scope(vault):
    out = find("GIZMO", "--vault", str(vault))
    assert "topics/gizmo.md" in out and "tasks.md" in out and "projects/acme/_project.md" in out
    assert "sources/raw.md" not in out and "install/" not in out and "AGENTS.md" not in out
    assert "sources/raw.md" in find("gizmo", "--vault", str(vault), "--sources")


def test_distinct_terms_outrank_hit_count(vault):
    out = find("gizmo widget", "--vault", str(vault))
    assert out.index("projects/acme/_project.md") < out.index("topics/noise.md")


def test_path_match_boosts(vault):
    out = find("jane widget", "--vault", str(vault))
    assert out.index("people/jane-doe.md") < out.index("topics/noise.md")


def test_long_line_cut_to_window(vault):
    write(vault, "topics/long.md", "# Long\n" + "a" * 3000 + " needle " + "b" * 3000 + "\n")
    out = find("needle", "--vault", str(vault))
    line = next(x for x in out.splitlines() if "needle" in x)
    assert len(line) < 300 and "…" in line


def test_output_capped_with_tail(vault):
    for i in range(60):
        write(vault, f"meetings/2026-01-{i:02d}-m.md", f"# M{i}\n## Notes\nThe gizmo came up again in meeting {i}.\n")
    out = find("gizmo", "--vault", str(vault), "--max-bytes", "1500")
    tail = out.splitlines()[-1]
    assert len(out.encode()) < 1800
    assert "not shown" in tail and "narrow" in tail


def test_no_hits(vault):
    assert find("zzzqqq", "--vault", str(vault)).splitlines()[-1].startswith("[find] 0 sections, 0 hits")


def test_default_vault_is_home_brain(vault, tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    (home / "brain").symlink_to(vault)
    assert "topics/gizmo.md" in find("gizmo", home=home)


def test_slug_page_outranks_busier_page_with_same_terms(vault):
    write(vault, "people/nora-quist.md", "# Nora Quist\nAE.\n")
    write(vault, "projects/busy/_project.md", "## Log\n" + "Nora Quist said so.\n" * 20)
    out = find("who is Nora Quist", "--vault", str(vault))
    assert out.index("people/nora-quist.md") < out.index("projects/busy/_project.md")


def test_hyphen_and_underscore_match_each_other(vault):
    write(vault, "projects/parts-wiki/_project.md", "# Parts\nThe parts_wiki tool.\n")
    out = find("parts-wiki", "--vault", str(vault))
    assert "2: The parts_wiki tool." in out


def test_top_folder_name_is_not_a_slug_match(vault):
    out = find("people widget", "--vault", str(vault))
    assert out.index("topics/noise.md") < out.index("people/jane-doe.md")


def test_last_section_ends_at_last_line(vault):
    assert "topics/gizmo.md:4-5 " in find("gizmo", "--vault", str(vault))


def test_repeated_term_counts_once(vault):
    assert "[1/1 terms" in find("gizmo gizmo", "--vault", str(vault))


def test_yaml_comments_are_not_headings(vault):
    write(vault, "projects/acme/plan.data.yml", "# comment\nflat: gizmo\n")
    assert "plan.data.yml:1-2 (0.0 KB) (top)" in find("gizmo", "--vault", str(vault))


def test_equal_meetings_newest_first(vault):
    write(vault, "meetings/2026-01-01-a.md", "orbit\n")
    write(vault, "meetings/2026-03-01-b.md", "orbit\n")
    out = find("orbit", "--vault", str(vault))
    assert out.index("2026-03-01-b") < out.index("2026-01-01-a")


def test_plural_term_matches_singular(vault):
    write(vault, "topics/tips.md", "# Tips\nOne Gotcha here.\n")
    assert "topics/tips.md" in find("gotchas", "--vault", str(vault))


def test_frontmatter_is_not_searched(vault):
    out = find("name", "--vault", str(vault))
    assert out.splitlines()[-1].startswith("[find] 0 sections")


def test_line_numbers_stay_correct_after_frontmatter(vault):
    assert "11: Wave B ships the Gizmo widget." in find("wave", "--vault", str(vault))


def test_best_single_line_outranks_section_wide_spread(vault):
    write(vault, "projects/big/_project.md", "## Log\nalpha\nbeta\ngamma\n" + "alpha\n" * 10)
    write(vault, "topics/answer.md", "# Answer\nalpha beta here\n")
    out = find("alpha beta gamma", "--vault", str(vault))
    assert out.index("topics/answer.md") < out.index("projects/big/_project.md")


def test_busy_section_shows_lines_with_most_terms(vault):
    write(vault, "topics/busy.md", "# Busy\n" + "alpha\n" * 7 + "alpha beta answer\n")
    out = find("alpha beta", "--vault", str(vault))
    assert "9: alpha beta answer" in out
    assert out.index("2: alpha") < out.index("9: alpha beta answer")
