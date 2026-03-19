"""Unit tests for orchestrator.py TM-mode validation logic.

Tests the task.json-based validation that replaced the old README regex
approach. Orchestrator now reads task-type and level from task.json.
"""

import json
import tempfile
import unittest
from pathlib import Path


def _write_task_json(directory: Path, task_type: str, level: str) -> Path:
    """Write a minimal task.json to directory and return its path."""
    data = {
        "task-type": task_type,
        "status": "—",
        "level": level,
        "complexity": "—",
    }
    path = directory / "task.json"
    path.write_text(json.dumps(data, indent=2) + "\n")
    return path


def _validate_entry_point(task_json: Path, resume: bool = False) -> tuple[bool, str]:
    """Replicate the orchestrator TM validation logic.

    Returns (valid, error_message).
    """
    if not task_json.exists():
        return False, "task.json not found"
    try:
        data = json.loads(task_json.read_text())
    except Exception as e:
        return False, f"Failed to parse task.json: {e}"

    if data.get("task-type") != "PIPELINE-SUBTASK":
        return False, f"task-type is '{data.get('task-type')}', expected 'PIPELINE-SUBTASK'"

    if not resume and data.get("level") != "TOP":
        return False, f"level is '{data.get('level')}', expected 'TOP'"

    return True, ""


# ---------------------------------------------------------------------------
# task-type validation
# ---------------------------------------------------------------------------

class TestTaskTypeValidation(unittest.TestCase):
    def test_pipeline_subtask_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            task_json = _write_task_json(Path(tmp), "PIPELINE-SUBTASK", "TOP")
            valid, msg = _validate_entry_point(task_json)
            self.assertTrue(valid, msg)

    def test_user_task_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            task_json = _write_task_json(Path(tmp), "USER-TASK", "TOP")
            valid, msg = _validate_entry_point(task_json)
            self.assertFalse(valid)
            self.assertIn("task-type", msg)

    def test_user_subtask_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            task_json = _write_task_json(Path(tmp), "USER-SUBTASK", "TOP")
            valid, msg = _validate_entry_point(task_json)
            self.assertFalse(valid)

    def test_missing_task_json_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            valid, msg = _validate_entry_point(Path(tmp) / "task.json")
            self.assertFalse(valid)
            self.assertIn("not found", msg)


# ---------------------------------------------------------------------------
# Level: TOP validation
# ---------------------------------------------------------------------------

class TestLevelValidation(unittest.TestCase):
    def test_top_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            task_json = _write_task_json(Path(tmp), "PIPELINE-SUBTASK", "TOP")
            valid, msg = _validate_entry_point(task_json)
            self.assertTrue(valid, msg)

    def test_internal_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            task_json = _write_task_json(Path(tmp), "PIPELINE-SUBTASK", "INTERNAL")
            valid, msg = _validate_entry_point(task_json)
            self.assertFalse(valid)
            self.assertIn("level", msg)

    def test_dash_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            task_json = _write_task_json(Path(tmp), "PIPELINE-SUBTASK", "—")
            valid, msg = _validate_entry_point(task_json)
            self.assertFalse(valid)

    def test_internal_passes_with_resume(self):
        """--resume skips the Level:TOP check."""
        with tempfile.TemporaryDirectory() as tmp:
            task_json = _write_task_json(Path(tmp), "PIPELINE-SUBTASK", "INTERNAL")
            valid, msg = _validate_entry_point(task_json, resume=True)
            self.assertTrue(valid, msg)


# ---------------------------------------------------------------------------
# Combined validation
# ---------------------------------------------------------------------------

class TestCombinedValidation(unittest.TestCase):
    def test_valid_entry_point(self):
        with tempfile.TemporaryDirectory() as tmp:
            task_json = _write_task_json(Path(tmp), "PIPELINE-SUBTASK", "TOP")
            valid, msg = _validate_entry_point(task_json)
            self.assertTrue(valid, msg)

    def test_user_task_fails_type_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            task_json = _write_task_json(Path(tmp), "USER-TASK", "TOP")
            valid, _ = _validate_entry_point(task_json)
            self.assertFalse(valid)

    def test_internal_pipeline_subtask_fails_level(self):
        with tempfile.TemporaryDirectory() as tmp:
            task_json = _write_task_json(Path(tmp), "PIPELINE-SUBTASK", "INTERNAL")
            valid, _ = _validate_entry_point(task_json)
            self.assertFalse(valid)

    def test_malformed_json_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "task.json"
            p.write_text("{not valid json")
            valid, msg = _validate_entry_point(p)
            self.assertFalse(valid)
            self.assertIn("parse", msg)


if __name__ == "__main__":
    unittest.main()
