"""Unit tests for render_readme.py"""

import json
import unittest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "ai-builder" / "orchestrator"))

from render_readme import render_task_readme, _fmt_elapsed_s


class TestFmtElapsedS(unittest.TestCase):
    def test_seconds_only(self):
        self.assertEqual(_fmt_elapsed_s(45), "45s")

    def test_minutes_and_seconds(self):
        self.assertEqual(_fmt_elapsed_s(125), "2m 05s")

    def test_zero(self):
        self.assertEqual(_fmt_elapsed_s(0), "0s")

    def test_exact_minute(self):
        self.assertEqual(_fmt_elapsed_s(60), "1m 00s")


class TestRenderTopLevel(unittest.TestCase):
    def _write_and_render(self, tmp_path, data):
        task_json = tmp_path / "task.json"
        task_json.write_text(json.dumps(data))
        render_task_readme(task_json)
        return (tmp_path / "README.md").read_text()

    def test_title_uses_parent_field(self, tmp_path=None):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            content = self._write_and_render(Path(d), {
                "level": "TOP", "parent": "my-service", "name": "build-1"
            })
            self.assertIn("# my-service", content)

    def test_title_falls_back_to_name(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            content = self._write_and_render(Path(d), {
                "level": "TOP", "name": "build-1"
            })
            self.assertIn("# build-1", content)

    def test_title_falls_back_to_goal_first_line(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            content = self._write_and_render(Path(d), {
                "level": "TOP", "goal": "Build a user service.\nMore context."
            })
            self.assertIn("# Build a user service.", content)

    def test_run_summary_rendered(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            content = self._write_and_render(Path(d), {
                "level": "TOP",
                "parent": "svc",
                "run_summary": {
                    "start": "2026-01-01 10:00",
                    "end": "2026-01-01 10:05",
                    "elapsed_s": 300,
                    "total_tokens_in": 1000,
                    "total_tokens_out": 500,
                    "total_tokens_cached": 200,
                    "invocation_count": 3,
                },
            })
            self.assertIn("## Run Summary", content)
            self.assertIn("5m 00s", content)
            self.assertIn("1,000", content)

    def test_no_run_summary_section_when_absent(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            content = self._write_and_render(Path(d), {"level": "TOP", "parent": "svc"})
            self.assertNotIn("## Run Summary", content)

    def test_execution_log_rendered(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            content = self._write_and_render(Path(d), {
                "level": "TOP",
                "parent": "svc",
                "execution_log": [{
                    "role": "ARCHITECT",
                    "agent": "claude",
                    "description": "design user-service",
                    "outcome": "DESIGN_READY",
                    "elapsed_s": 42,
                    "tokens_in": 100,
                    "tokens_out": 200,
                    "tokens_cached": 50,
                }],
            })
            self.assertIn("## Execution Log", content)
            self.assertIn("ARCHITECT", content)
            self.assertIn("DESIGN_READY", content)

    def test_subtask_list_rendered(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            content = self._write_and_render(Path(d), {
                "level": "TOP",
                "parent": "svc",
                "subtasks": [
                    {"name": "auth", "complete": False},
                    {"name": "db", "complete": True},
                ],
            })
            self.assertIn("## Subtasks", content)
            self.assertIn("- [ ] auth", content)
            self.assertIn("- [x] db", content)

    def test_missing_task_json_does_not_raise(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            # Should silently return without writing anything
            render_task_readme(Path(d) / "nonexistent.json")
            self.assertFalse((Path(d) / "README.md").exists())

    def test_malformed_json_does_not_raise(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            task_json = Path(d) / "task.json"
            task_json.write_text("{not valid json")
            render_task_readme(task_json)  # should not raise


class TestRenderSubtask(unittest.TestCase):
    def _write_and_render(self, tmp_path, data):
        task_json = tmp_path / "task.json"
        task_json.write_text(json.dumps(data))
        render_task_readme(task_json)
        return (tmp_path / "README.md").read_text()

    def test_basic_subtask_renders_goal_and_context(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            content = self._write_and_render(Path(d), {
                "level": "LEAF",
                "name": "build-auth",
                "goal": "Implement JWT auth.",
                "context": "Part of user-service.",
            })
            self.assertIn("# build-auth", content)
            self.assertIn("## Goal", content)
            self.assertIn("Implement JWT auth.", content)
            self.assertIn("## Context", content)

    def test_test_command_block_rendered(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            content = self._write_and_render(Path(d), {
                "level": "LEAF",
                "name": "x",
                "test_command": "go test ./...",
            })
            self.assertIn("## Test Command", content)
            self.assertIn("go test ./...", content)

    def test_design_and_acceptance_criteria_rendered(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            content = self._write_and_render(Path(d), {
                "level": "LEAF",
                "name": "x",
                "design": "## Design\nUse repository pattern.",
                "acceptance_criteria": "## Acceptance Criteria\n- Tests pass.",
            })
            self.assertIn("## Design", content)
            self.assertIn("## Acceptance Criteria", content)

    def test_empty_optional_fields_omitted(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            content = self._write_and_render(Path(d), {
                "level": "LEAF",
                "name": "x",
                "goal": "",
                "context": "",
                "design": "",
                "test_command": "",
            })
            self.assertNotIn("## Goal", content)
            self.assertNotIn("## Context", content)
            self.assertNotIn("## Test Command", content)


if __name__ == "__main__":
    unittest.main()
