"""Unit tests for ai-builder/orchestrator/metrics.py."""

import json
import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path

# Allow importing from the orchestrator directory without installation.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "ai-builder" / "orchestrator"))

from metrics import (
    InvocationRecord,
    RunData,
    _fmt_elapsed,
    _build_summary_lines,
    description_from_job_path,
    record_invocation,
    update_task_doc,
    write_metrics_to_task_json,
    write_summary_to_readme,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_inv(role="ARCHITECT", agent="claude", n=1, description="build-1",
              seconds=60, tokens_in=100, tokens_out=50, tokens_cached=0,
              outcome="ARCHITECT_DESIGN_READY") -> InvocationRecord:
    start = datetime(2025, 1, 1, 10, 0, 0)
    end = start + timedelta(seconds=seconds)
    return InvocationRecord(
        role=role, agent=agent, n=n, description=description,
        start=start, end=end, elapsed=timedelta(seconds=seconds),
        tokens_in=tokens_in, tokens_out=tokens_out, tokens_cached=tokens_cached,
        outcome=outcome,
    )


def _make_run(*invocations) -> RunData:
    run = RunData(task_name="build-1", start=datetime(2025, 1, 1, 10, 0, 0))
    run.invocations = list(invocations)
    run.end = datetime(2025, 1, 1, 10, 5, 0)
    return run


# ---------------------------------------------------------------------------
# _fmt_elapsed
# ---------------------------------------------------------------------------

class TestFmtElapsed(unittest.TestCase):
    def test_sub_minute(self):
        self.assertEqual(_fmt_elapsed(timedelta(seconds=47)), "47s")

    def test_zero_seconds(self):
        self.assertEqual(_fmt_elapsed(timedelta(seconds=0)), "0s")

    def test_exactly_one_minute(self):
        self.assertEqual(_fmt_elapsed(timedelta(seconds=60)), "1m 00s")

    def test_mixed(self):
        self.assertEqual(_fmt_elapsed(timedelta(seconds=125)), "2m 05s")

    def test_large(self):
        self.assertEqual(_fmt_elapsed(timedelta(seconds=3661)), "61m 01s")


# ---------------------------------------------------------------------------
# description_from_job_path
# ---------------------------------------------------------------------------

class TestDescriptionFromJobPath(unittest.TestCase):
    def test_none_returns_dash(self):
        self.assertEqual(description_from_job_path(None), "—")

    def test_incremental_subtask_prefix(self):
        p = Path("/repo/project/tasks/main/in-progress/51de6e-0001-handler/README.md")
        self.assertEqual(description_from_job_path(p), "handler")

    def test_toplevel_prefix(self):
        p = Path("/repo/project/tasks/main/in-progress/fa3480-build-1/README.md")
        self.assertEqual(description_from_job_path(p), "build-1")

    def test_no_prefix(self):
        p = Path("/repo/something/plain-name/README.md")
        self.assertEqual(description_from_job_path(p), "plain-name")

    def test_six_hex_prefix_only(self):
        p = Path("/repo/eab6f7-user-service/README.md")
        self.assertEqual(description_from_job_path(p), "user-service")

    def test_incremental_wins_over_toplevel(self):
        # Directory matches both patterns; incremental (4-digit) should win.
        p = Path("/repo/abc123-0042-my-task/README.md")
        self.assertEqual(description_from_job_path(p), "my-task")


# ---------------------------------------------------------------------------
# record_invocation
# ---------------------------------------------------------------------------

class TestRecordInvocation(unittest.TestCase):
    def test_appends_to_run(self):
        run = RunData(task_name="t", start=datetime.now())
        start = datetime(2025, 1, 1, 9, 0, 0)
        end = datetime(2025, 1, 1, 9, 1, 5)
        inv = record_invocation(
            run=run, role="ARCHITECT", agent="claude", role_counter=1,
            description="build-1", start=start, end=end,
            tokens_in=200, tokens_out=80, tokens_cached=10, outcome="ARCH_DONE",
        )
        self.assertEqual(len(run.invocations), 1)
        self.assertIs(run.invocations[0], inv)
        self.assertEqual(inv.elapsed, timedelta(seconds=65))
        self.assertEqual(inv.n, 1)
        self.assertEqual(inv.tokens_in, 200)
        self.assertEqual(inv.tokens_cached, 10)

    def test_multiple_invocations(self):
        run = RunData(task_name="t", start=datetime.now())
        for i in range(3):
            record_invocation(run, "TESTER", "claude", i + 1, "desc",
                              datetime.now(), datetime.now(), 0, 0, 0, "OUT")
        self.assertEqual(len(run.invocations), 3)


# ---------------------------------------------------------------------------
# _build_summary_lines
# ---------------------------------------------------------------------------

class TestBuildSummaryLines(unittest.TestCase):
    def setUp(self):
        self.inv = _make_inv(tokens_in=1000, tokens_out=500, tokens_cached=200)
        self.run = _make_run(self.inv)
        self.lines = _build_summary_lines(self.run)
        self.text = "\n".join(self.lines)

    def test_contains_task_name(self):
        self.assertIn("build-1", self.text)

    def test_contains_token_totals(self):
        self.assertIn("1,000", self.text)   # tokens_in
        self.assertIn("500", self.text)     # tokens_out
        self.assertIn("200", self.text)     # tokens_cached
        self.assertIn("1,700", self.text)   # total

    def test_contains_invocations_section(self):
        self.assertIn("### Invocations", self.text)

    def test_contains_per_role_totals(self):
        self.assertIn("### Per-Role Totals", self.text)

    def test_contains_token_usage_by_role(self):
        self.assertIn("### Token Usage by Role", self.text)

    def test_contains_invocations_by_agent(self):
        self.assertIn("### Invocations by Agent", self.text)

    def test_grand_total_row_present(self):
        self.assertIn("**Total**", self.text)

    def test_elapsed_format(self):
        self.assertIn("1m 00s", self.text)

    def test_multiple_roles(self):
        run = _make_run(
            _make_inv(role="ARCHITECT", seconds=60),
            _make_inv(role="IMPLEMENTOR", seconds=90),
            _make_inv(role="TESTER", seconds=30),
        )
        lines = _build_summary_lines(run)
        text = "\n".join(lines)
        self.assertIn("ARCHITECT", text)
        self.assertIn("IMPLEMENTOR", text)
        self.assertIn("TESTER", text)


# ---------------------------------------------------------------------------
# update_task_doc
# ---------------------------------------------------------------------------

class TestUpdateTaskDoc(unittest.TestCase):
    def _readme_with_section(self, tmp_path: Path) -> Path:
        p = tmp_path / "README.md"
        p.write_text(
            "# Task: build-1\n\n"
            "## Goal\n\nDo the thing.\n\n"
            "## Execution Log\n\n"
            "| # | Role | Agent | Description | Ended | Elapsed | Tokens In | Tokens Out | Tokens Cached |\n"
            "|---|------|-------|-------------|-------|---------|-----------|------------|---------------|\n"
        )
        return p

    def _readme_without_section(self, tmp_path: Path) -> Path:
        p = tmp_path / "README.md"
        p.write_text(
            "# Task: build-1\n\n"
            "## Goal\n\nDo the thing.\n\n"
            "## Context\n\nSome context.\n"
        )
        return p

    def test_rewrites_existing_section(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            p = self._readme_with_section(Path(d))
            run = _make_run(_make_inv())
            update_task_doc(p, run)
            content = p.read_text()
            self.assertIn("ARCHITECT", content)
            self.assertIn("| 1 |", content)

    def test_inserts_section_if_absent(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            p = self._readme_without_section(Path(d))
            run = _make_run(_make_inv())
            update_task_doc(p, run)
            content = p.read_text()
            self.assertIn("## Execution Log", content)
            self.assertIn("ARCHITECT", content)
            # Original sections should still be present
            self.assertIn("## Goal", content)
            self.assertIn("## Context", content)

    def test_section_inserted_after_goal(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            p = self._readme_without_section(Path(d))
            run = _make_run(_make_inv())
            update_task_doc(p, run)
            content = p.read_text()
            goal_pos = content.index("## Goal")
            log_pos = content.index("## Execution Log")
            self.assertGreater(log_pos, goal_pos)

    def test_noop_if_file_missing(self):
        # Should not raise
        update_task_doc(Path("/nonexistent/README.md"), _make_run(_make_inv()))

    def test_row_count_matches_invocations(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            p = self._readme_with_section(Path(d))
            run = _make_run(
                _make_inv(role="ARCHITECT"),
                _make_inv(role="IMPLEMENTOR"),
                _make_inv(role="TESTER"),
            )
            update_task_doc(p, run)
            content = p.read_text()
            # Each data row starts with "| N |"
            self.assertIn("| 1 |", content)
            self.assertIn("| 2 |", content)
            self.assertIn("| 3 |", content)


# ---------------------------------------------------------------------------
# write_metrics_to_task_json
# ---------------------------------------------------------------------------

class TestWriteMetricsToTaskJson(unittest.TestCase):
    def _make_task_json(self, tmp_path: Path) -> Path:
        p = tmp_path / "task.json"
        p.write_text(json.dumps({"task-type": "PIPELINE-SUBTASK", "level": "TOP"}, indent=2))
        return p

    def test_writes_execution_log(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            p = self._make_task_json(Path(d))
            run = _make_run(_make_inv(tokens_in=42, tokens_out=7, tokens_cached=3))
            write_metrics_to_task_json(p, run)
            data = json.loads(p.read_text())
            self.assertIn("execution_log", data)
            self.assertEqual(len(data["execution_log"]), 1)
            inv = data["execution_log"][0]
            self.assertEqual(inv["tokens_in"], 42)
            self.assertEqual(inv["tokens_out"], 7)
            self.assertEqual(inv["tokens_cached"], 3)
            self.assertIn("elapsed_s", inv)
            self.assertIn("start", inv)
            self.assertIn("end", inv)

    def test_no_run_summary_unless_final(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            p = self._make_task_json(Path(d))
            run = _make_run(_make_inv())
            write_metrics_to_task_json(p, run, final=False)
            data = json.loads(p.read_text())
            self.assertNotIn("run_summary", data)

    def test_run_summary_written_when_final(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            p = self._make_task_json(Path(d))
            run = _make_run(_make_inv(tokens_in=100, tokens_out=50, tokens_cached=10))
            write_metrics_to_task_json(p, run, final=True)
            data = json.loads(p.read_text())
            self.assertIn("run_summary", data)
            rs = data["run_summary"]
            self.assertEqual(rs["total_tokens_in"], 100)
            self.assertEqual(rs["total_tokens_out"], 50)
            self.assertEqual(rs["total_tokens_cached"], 10)
            self.assertEqual(rs["invocation_count"], 1)
            self.assertIn("elapsed_s", rs)
            self.assertIn("start", rs)
            self.assertIn("end", rs)

    def test_noop_if_file_missing(self):
        # Should not raise
        write_metrics_to_task_json(Path("/nonexistent/task.json"), _make_run(_make_inv()))

    def test_preserves_existing_fields(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            p = self._make_task_json(Path(d))
            run = _make_run(_make_inv())
            write_metrics_to_task_json(p, run)
            data = json.loads(p.read_text())
            self.assertEqual(data["task-type"], "PIPELINE-SUBTASK")
            self.assertEqual(data["level"], "TOP")


# ---------------------------------------------------------------------------
# write_summary_to_readme
# ---------------------------------------------------------------------------

class TestWriteSummaryToReadme(unittest.TestCase):
    def test_appends_section(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "README.md"
            p.write_text("# Task: build-1\n\n## Goal\n\nDo the thing.\n")
            run = _make_run(_make_inv())
            write_summary_to_readme(p, run)
            content = p.read_text()
            self.assertIn("## Run Summary", content)
            self.assertIn("### Invocations", content)
            # Original content preserved
            self.assertIn("## Goal", content)

    def test_noop_if_file_missing(self):
        write_summary_to_readme(Path("/nonexistent/README.md"), _make_run(_make_inv()))


if __name__ == "__main__":
    unittest.main()
