import datetime as dt
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import unittest

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extract.py")
SECRET = "sk-" + "abcdefghijklmnopqrstuvwx"


def iso(days_ago):
    t = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days_ago)
    return t.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def prompt(uid, ago, text):
    return {"type": "user", "uuid": uid, "timestamp": iso(ago), "cwd": "/work/demo",
            "message": {"role": "user", "content": text}}


def say(uid, ago, text="", tool=None):
    blocks = [{"type": "text", "text": text}] if text else []
    if tool:
        blocks.append({"type": "tool_use", "id": tool[0], "name": "Bash", "input": {"command": tool[1]}})
    return {"type": "assistant", "uuid": uid, "timestamp": iso(ago),
            "message": {"id": "m-" + uid, "role": "assistant", "content": blocks}}


def result(uid, ago, tool_id, text, error=False, **extra):
    return dict({"type": "user", "uuid": uid, "timestamp": iso(ago),
                 "message": {"role": "user", "content": [
                     {"type": "tool_result", "tool_use_id": tool_id, "content": text, "is_error": error}]}},
                **extra)


SESSION = [
    say("a0", 10, "Here is the summary."),
    prompt("u0", 10, "that's wrong, you missed the second file"),
    prompt("u1", 2, "please list the files"),
    say("a1", 2, "I will run the tool.", ("t1", "mytool run --x")),
    result("r1", 2, "t1", "Exit code 1\nmytool: error: unknown flag --x", error=True),
    say("a2", 2, tool=("t2", "mytool run --y")),
    result("r2", 2, "t2", "listed 3 files"),
    prompt("u2", 2, f"no, that's wrong, I said list them all. key {SECRET}"),
    say("a3", 2, "Running a long scan of the disk."),
    prompt("u3", 2, "[Request interrupted by user]"),
    prompt("u4", 2, "you forgot the hidden files, why did you skip them"),
    say("a4", 2, tool=("t3", "rm -rf build")),
    result("r3", 2, "t3", "The user doesn't want to proceed with this tool use.",
           toolDenialKind="user-rejected", userFeedback="never delete without asking"),
]


class ExtractTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.projects = os.path.join(self.tmp.name, "projects")
        proj = os.path.join(self.projects, "-work-demo")
        os.makedirs(proj)
        with open(os.path.join(proj, "s1.jsonl"), "w", encoding="utf-8") as fh:
            fh.write("\n".join(json.dumps(r) for r in SESSION) + "\n")
        stale = os.path.join(proj, "s0.jsonl")
        with open(stale, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(prompt("x0", 40, "that's wrong, you broke it")) + "\n")
        old = time.time() - 40 * 86400
        os.utime(stale, (old, old))

    def tearDown(self):
        self.tmp.cleanup()

    def run_extract(self, *args, projects=None):
        out = os.path.join(self.tmp.name, "digest.md")
        p = subprocess.run([sys.executable, SCRIPT, "--projects-dir", projects or self.projects,
                            "--out", out, *args],
                           capture_output=True, text=True, check=True,
                           env=dict(os.environ, HOME=self.tmp.name))
        with open(out, encoding="utf-8") as fh:
            return json.loads(p.stderr.strip().splitlines()[-1]), fh.read()

    def test_core_signals_in_default_window(self):
        stats, digest = self.run_extract()
        self.assertEqual(stats["days"], 7)
        self.assertEqual(stats["corrections"][0], 1)
        self.assertEqual(stats["interrupts"][0], 1)
        self.assertEqual(stats["rejections"][0], 1)
        self.assertEqual(stats["errors"][0], 1)
        self.assertEqual(stats["retries"][0], 1)
        self.assertIn("I said list them all", digest)
        self.assertIn("you forgot the hidden files", digest)
        self.assertIn("never delete without asking", digest)
        self.assertIn("mytool: error: unknown flag", digest)
        self.assertIn("`mytool run` failed then re-run 1x", digest)
        self.assertNotIn("you missed the second file", digest)

    def test_redacts_secrets(self):
        _, digest = self.run_extract()
        self.assertNotIn(SECRET, digest)
        self.assertIn("[REDACTED]", digest)
        self.assertNotIn("<redacted>", digest)

    def test_days_window_widens_and_clamps_to_30(self):
        stats, digest = self.run_extract("--days", "99")
        self.assertEqual(stats["days"], 30)
        self.assertEqual(stats["corrections"][0], 2)
        self.assertIn("you missed the second file", digest)
        self.assertNotIn("you broke it", digest)
        self.assertNotIn("Too few signals", digest)

    def test_too_few_signals_says_so(self):
        empty = os.path.join(self.tmp.name, "none")
        os.makedirs(empty)
        stats, digest = self.run_extract(projects=empty)
        self.assertEqual(stats["signals"], 0)
        self.assertIn("Too few signals", digest)

    def write_lines(self, relpath, lines, age_secs=0):
        path = os.path.join(self.projects, "-work-demo", relpath)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
        if age_secs:
            t = time.time() - age_secs
            os.utime(path, (t, t))

    def test_skips_malformed_and_non_object_lines(self):
        self.write_lines("s2.jsonl", [
            "not json", "[1, 2]", "42", "null", '"text"',
            json.dumps(prompt("m1", 2, "that's wrong, you missed the other file"))])
        stats, digest = self.run_extract()
        self.assertEqual(stats["corrections"][0], 2)
        self.assertIn("you missed the other file", digest)

    def test_null_timestamp_and_cwd(self):
        self.write_lines("s2.jsonl", [
            json.dumps(dict(prompt("n1", 2, "ignored"), timestamp=None, cwd=None)),
            json.dumps(prompt("n2", 2, "that's wrong, you missed the other file"))])
        stats, _ = self.run_extract()
        self.assertEqual(stats["corrections"][0], 2)

    def test_subagent_tool_errors_are_counted(self):
        self.write_lines("sess1/subagents/agent-abc.jsonl", [
            json.dumps(say("g1", 2, tool=("gt1", "subtool go"))),
            json.dumps(result("gr1", 2, "gt1", "subtool: fatal: boom", error=True))], age_secs=3600)
        stats, digest = self.run_extract()
        self.assertEqual(stats["errors"][0], 2)
        self.assertIn("subtool: fatal: boom", digest)

    def test_recent_subagent_file_is_skipped_as_live(self):
        self.write_lines("sess1/subagents/agent-abc.jsonl", [
            json.dumps(say("g1", 2, tool=("gt1", "subtool go"))),
            json.dumps(result("gr1", 2, "gt1", "subtool: fatal: boom", error=True))])
        stats, _ = self.run_extract()
        self.assertEqual(stats["errors"][0], 1)

    def test_headless_sdk_cli_session_is_skipped(self):
        self.write_lines("s2.jsonl", [
            json.dumps(dict(prompt("h1", 2, "that's wrong, you headless thing"), entrypoint="sdk-cli"))])
        stats, digest = self.run_extract()
        self.assertEqual(stats["corrections"][0], 1)
        self.assertNotIn("headless thing", digest)

    def test_resumed_file_does_not_double_count(self):
        self.write_lines("s2.jsonl", [json.dumps(r) for r in SESSION])
        stats, _ = self.run_extract()
        self.assertEqual(stats["corrections"][0], 1)
        self.assertEqual(stats["errors"][0], 1)
        self.assertEqual(stats["rejections"][0], 1)

    def test_digest_is_owner_only(self):
        self.run_extract()
        mode = stat.S_IMODE(os.stat(os.path.join(self.tmp.name, "digest.md")).st_mode)
        self.assertEqual(mode, 0o600)

    def test_missing_redaction_list_exits_non_zero(self):
        root = os.path.join(self.tmp.name, "copy")
        os.makedirs(os.path.join(root, "install", "skills", "retro", "scripts"))
        script = os.path.join(root, "install", "skills", "retro", "scripts", "extract.py")
        shutil.copy(SCRIPT, script)
        p = subprocess.run([sys.executable, script, "--projects-dir", self.projects],
                           capture_output=True, text=True)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("AGENTS.md", p.stderr)
        self.assertIn("Never store", p.stderr)


if __name__ == "__main__":
    unittest.main()
