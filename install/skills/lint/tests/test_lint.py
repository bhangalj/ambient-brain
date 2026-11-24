from conftest import ago, checks, tasks, write


def test_clean_vault_is_silent(vault, lint):
    assert lint(vault) == (0, [])


def test_index_cap_counts_characters_not_bytes(vault, lint):
    entry = "- [[topics/alpha]] — " + "→" * (80 - len("- [[topics/alpha]] — "))
    assert len(entry) == 80
    write(vault, "index.md", (vault / "index.md").read_text(encoding="utf-8").replace("- [[topics/alpha]] — alpha topic", entry))
    assert lint(vault) == (0, [])


def test_index_cap_fires_over_80(vault, lint):
    long = "- [[topics/alpha]] — " + "x" * 70
    write(vault, "index.md", (vault / "index.md").read_text(encoding="utf-8").replace("- [[topics/alpha]] — alpha topic", long))
    code, rows = lint(vault)
    assert code == 1
    assert rows == [["INDEX_CAP", "index.md:12", f"{len(long)} characters, cap 80"]]


def test_index_duplicate_line_fires(vault, lint):
    write(vault, "index.md", (vault / "index.md").read_text(encoding="utf-8") + "- [[topics/alpha]] — alpha topic\n")
    code, rows = lint(vault)
    assert code == 1 and checks(rows) == ["INDEX_DUP"]
    assert rows[0][1] == "index.md:14"


def test_index_hub_pointer_with_count_fires(vault, lint):
    write(vault, "index.md", (vault / "index.md").read_text(encoding="utf-8")
          .replace("colleagues, one line each (sharded)", "colleagues, 72 pages (sharded)"))
    code, rows = lint(vault)
    assert code == 1 and checks(rows) == ["INDEX_POINTER"]


def test_index_hub_pointer_with_date_range_fires(vault, lint):
    write(vault, "index.md", (vault / "index.md").read_text(encoding="utf-8")
          .replace("colleagues, one line each (sharded)", "colleagues 2026-07 to 2026-11"))
    assert checks(lint(vault)[1]) == ["INDEX_POINTER"]


def test_index_hub_pointer_with_quarter_label_is_not_flagged(vault, lint):
    write(vault, "index.md", (vault / "index.md").read_text(encoding="utf-8")
          .replace("colleagues, one line each (sharded)", "Q4 plan (sharded)"))
    assert lint(vault) == (0, [])


def test_frontmatter_missing_base_keys_fires(vault, lint):
    write(vault, "topics/beta.md", "---\ntype: topic\n---\nlinked from [[topics/alpha]]\n")
    write(vault, "topics/gamma.md", "no frontmatter at all [[topics/beta]]\n")
    write(vault, "topics/alpha.md", (vault / "topics/alpha.md").read_text() + "[[topics/gamma]]\n")
    code, rows = lint(vault)
    assert code == 1
    assert sorted(rows) == [["FRONTMATTER", "topics/beta.md", "missing updated"],
                            ["FRONTMATTER", "topics/gamma.md", "no frontmatter"]]


def test_frontmatter_bad_updated_date_fires(vault, lint):
    write(vault, "topics/alpha.md", (vault / "topics/alpha.md").read_text().replace("updated: 2026-01-01", "updated: Jan 2026"))
    assert lint(vault)[1] == [["FRONTMATTER", "topics/alpha.md", "updated is not YYYY-MM-DD: Jan 2026"]]


def test_frontmatter_per_type_keys_fire(vault, lint):
    write(vault, "people/jane-doe.md", "---\ntype: person\nupdated: 2026-01-01\n---\n")
    write(vault, "projects/acme/_project.md", "---\ntype: project\nname: Acme\nstatus: shipped\nupdated: 2026-01-01\n---\n[[projects/acme/plan]]\n")
    write(vault, "projects/acme/plan.md", "---\ntype: project-doc\nupdated: 2026-01-01\n---\n")
    write(vault, "meetings/2026-01-01-kickoff.md", "---\ntype: meeting\nupdated: 2026-01-01\n---\n[[sources/2026-01-01-kickoff]]\n")
    write(vault, "topics/alpha.md", "---\ntype: thing\nupdated: 2026-01-01\n---\n")
    assert sorted(lint(vault)[1]) == [
        ["FRONTMATTER", "meetings/2026-01-01-kickoff.md", "missing date"],
        ["FRONTMATTER", "people/jane-doe.md", "missing name"],
        ["FRONTMATTER", "projects/acme/_project.md", "status not in active|paused|done|idea: shipped"],
        ["FRONTMATTER", "projects/acme/plan.md", "missing project"],
        ["FRONTMATTER", "topics/alpha.md", "unknown type: thing"],
    ]


def test_frontmatter_meta_hub_needs_only_type_and_updated(vault, lint):
    write(vault, "topics/_index.md", "---\ntype: meta\nupdated: 2026-01-01\n---\n- [[topics/alpha]]\n")
    write(vault, "index.md", (vault / "index.md").read_text(encoding="utf-8") + "- [[topics/_index]] — topics (sharded)\n")
    assert lint(vault) == (0, [])


def test_broken_wikilink_fires(vault, lint):
    write(vault, "topics/alpha.md", (vault / "topics/alpha.md").read_text() + "\nSee [[people/nobody|Nobody]] and [[../sources/missing]].\n")
    assert lint(vault)[1] == [["BROKEN_LINK", "topics/alpha.md:11", "[[people/nobody|Nobody]]"],
                              ["BROKEN_LINK", "topics/alpha.md:11", "[[../sources/missing]]"]]


def test_broken_wikilink_in_frontmatter_relative_source_fires(vault, lint):
    (vault / "sources/2026-01-01-kickoff.md").unlink()
    assert lint(vault)[1] == [["BROKEN_LINK", "meetings/2026-01-01-kickoff.md:5", "[[../sources/2026-01-01-kickoff]]"]]


def test_links_to_folders_and_files_with_extension_resolve(vault, lint):
    write(vault, "sources/shots/a.png", "x")
    write(vault, "topics/alpha.md", (vault / "topics/alpha.md").read_text()
          + "\n[[sources/shots]] [[sources/2026-01-01-kickoff.md]] [[topics/alpha#Top]]\n")
    assert lint(vault) == (0, [])


def test_orphan_page_fires(vault, lint):
    write(vault, "topics/lonely.md", "---\ntype: topic\nupdated: 2026-01-01\n---\nI link to myself: [[topics/lonely]]\n")
    assert lint(vault)[1] == [["ORPHAN", "topics/lonely.md", "no inbound wikilink and no index entry"]]


def test_orphan_quiet_when_only_a_shard_hub_lists_it(vault, lint):
    write(vault, "people/john-roe.md", "---\ntype: person\nname: John Roe\nupdated: 2026-01-01\n---\n")
    write(vault, "people/_index.md", (vault / "people/_index.md").read_text() + "- [[people/john-roe]] — John\n")
    assert lint(vault) == (0, [])


def test_orphan_ignores_links_from_sources_and_install(vault, lint):
    write(vault, "topics/lonely.md", "---\ntype: topic\nupdated: 2026-01-01\n---\n")
    write(vault, "sources/note.md", "[[topics/lonely]]")
    write(vault, "install/x.md", "[[topics/lonely]]")
    write(vault, "topics/alpha.md", (vault / "topics/alpha.md").read_text() + "[[sources/note]]\n")
    assert lint(vault)[1] == [["ORPHAN", "topics/lonely.md", "no inbound wikilink and no index entry"]]


def test_undistilled_source_fires(vault, lint):
    write(vault, "sources/2026-02-02-forgotten.md", "raw")
    assert lint(vault)[1] == [["UNDISTILLED", "sources/2026-02-02-forgotten.md", "no page cites it and no SKIPPED.md lists it"]]


def test_undistilled_quiet_for_skips_infra_and_folders(vault, lint):
    write(vault, "sources/SKIPPED.md", "# Skipped\nProse naming `run.sh` and `2026-02-02-prose`.\n- `2026-02-02-general.md` — noise\n")
    write(vault, "sources/transcripts/SKIPPED.md", "- `2026-02-02/123_standup.md` — standup\n")
    write(vault, "sources/transcripts/2026-02-02/123_standup.md", "raw")
    write(vault, "sources/transcripts/INDEX.md", "")
    write(vault, "sources/2026-02-02-general.md", "raw")
    write(vault, "sources/shots/one.png", "x")
    write(vault, "sources/shots/two.png", "x")
    write(vault, "topics/alpha.md", (vault / "topics/alpha.md").read_text() + "\nCaptures: `sources/shots/`.\n")
    assert lint(vault) == (0, [])


def test_undistilled_prose_backticks_in_skipped_do_not_hide_sources(vault, lint):
    write(vault, "sources/SKIPPED.md", "Prose naming `2026-02-02-prose`.\n")
    write(vault, "sources/2026-02-02-prose.md", "raw")
    assert checks(lint(vault)[1]) == ["UNDISTILLED"]


def test_tasks_stray_line_before_first_heading_fires(vault, lint):
    write(vault, "tasks.md", tasks(head=f"> `## Now`- **Wedged task** — [[topics/alpha]] ({ago(1)})\n- Loose task ({ago(1)})\n"))
    rows = lint(vault)[1]
    assert checks(rows) == ["TASKS_STRAY", "TASKS_STRAY"]
    assert [r[1] for r in rows] == ["tasks.md:8", "tasks.md:9"]


def test_tasks_header_template_line_is_not_stray(vault, lint):
    write(vault, "tasks.md", tasks(head="> `- <task> — [[meetings/YYYY-MM-DD-<slug>|src]] (YYYY-MM-DD)`\n"))
    assert lint(vault) == (0, [])


def test_tasks_headings_fire(vault, lint):
    text = (tasks().replace("## Blocked", "## Someday").replace("## Later", "## TMP").replace("## Personal", "## Later")
            .replace("## TMP", "## Personal") + "## Now\n")
    write(vault, "tasks.md", text)
    rows = lint(vault)[1]
    details = [r[2] for r in rows if r[0] == "TASKS_HEADINGS"]
    assert details == ["unknown heading: ## Someday", "## Later out of order", "duplicate heading: ## Now", "missing heading: ## Blocked"]


def test_tasks_now_cap_fires_on_eighth(vault, lint):
    now = [f"- item {i} ({ago(1)})" for i in range(8)]
    write(vault, "tasks.md", tasks(now=now))
    assert lint(vault)[1] == [["TASKS_NOW_CAP", "tasks.md:17", "8 items in ## Now, cap 7"]]


def test_tasks_now_cap_quiet_at_seven_with_subbullets(vault, lint):
    now = [f"- item {i} ({ago(1)})" for i in range(7)] + ["  - sub-step", "  - another sub-step"]
    write(vault, "tasks.md", tasks(now=now))
    assert lint(vault) == (0, [])


def test_tasks_blocked_without_waiting_on_fires(vault, lint):
    write(vault, "tasks.md", tasks(blocked=[f"- Stuck on something ({ago(1)})"]))
    assert checks(lint(vault)[1]) == ["TASKS_BLOCKED"]


def test_tasks_waiting_on_outside_blocked_fires(vault, lint):
    write(vault, "tasks.md", tasks(next_=[f"- Chase (waiting on Bob) ({ago(1)})"], later=[f"- Chase (waiting on Ann) ({ago(1)})"]))
    assert checks(lint(vault)[1]) == ["TASKS_WAITING", "TASKS_WAITING"]


def test_tasks_expired_next_and_later_fire(vault, lint):
    write(vault, "tasks.md", tasks(next_=[f"- Old next ({ago(22)})"],
                                   later=[f"- Old later, wrapped", f"  over two lines ({ago(40)})"]))
    rows = lint(vault)[1]
    assert rows == [["TASKS_EXPIRED", "tasks.md:13", f"## Next line captured {ago(22)}, 22 days ago, no deadline"],
                    ["TASKS_EXPIRED", "tasks.md:19", f"## Later line captured {ago(40)}, 40 days ago, no deadline"]]


def test_tasks_expiry_quiet_with_deadline_or_recent(vault, lint):
    write(vault, "tasks.md", tasks(next_=[f"- ⏰ Ship it ({ago(30)})", f"- Do it by Mon 2026-12-07 ({ago(30)})",
                                          f"- Finish before 1 Dec ({ago(30)})", f"- Fresh ({ago(21)})"],
                                   later=[f"- Deferred {ago(40)}, then re-captured ({ago(2)})"]))
    assert lint(vault) == (0, [])


def test_tasks_expiry_quiet_for_other_deadline_forms(vault, lint):
    write(vault, "tasks.md", tasks(next_=[f"- Ship by Dec 7 ({ago(30)})", f"- Ship by ~1 Dec ({ago(30)})",
                                          f"- Ship by end of Nov ({ago(30)})"]))
    assert lint(vault) == (0, [])


def test_tasks_impossible_capture_date_is_reported(vault, lint):
    write(vault, "tasks.md", tasks(next_=["- Bad date (2026-02-30)"]))
    assert lint(vault)[1] == [["TASKS_DATE", "tasks.md:13", "capture date is not a real date: 2026-02-30"]]


def test_tasks_impossible_capture_date_under_now_is_reported(vault, lint):
    write(vault, "tasks.md", tasks(now=["- Bad date (2026-02-30)"]))
    assert lint(vault)[1] == [["TASKS_DATE", "tasks.md:10", "capture date is not a real date: 2026-02-30"]]
