"""Unit tests for orchestrator.py TM-mode validation logic.

Tests the regex patterns used to validate PIPELINE-SUBTASK and Level:TOP
fields without importing or running the orchestrator (which has top-level
side effects from argparse).
"""

import re
import unittest


# The exact patterns used in orchestrator.py TM validation block.
TASK_TYPE_PATTERN = r'\|\s*Task-type\s*\|\s*PIPELINE-SUBTASK\s*\|'
LEVEL_PATTERN      = r'\|\s*Level\s*\|\s*TOP\s*\|'


def _is_pipeline_subtask(content: str) -> bool:
    return bool(re.search(TASK_TYPE_PATTERN, content))


def _is_level_top(content: str) -> bool:
    return bool(re.search(LEVEL_PATTERN, content))


# ---------------------------------------------------------------------------
# Task-type validation
# ---------------------------------------------------------------------------

class TestTaskTypePattern(unittest.TestCase):
    def _table(self, task_type: str) -> str:
        return (
            f"| Field       | Value           |\n"
            f"|-------------|-----------------||\n"
            f"| Task-type   | {task_type}     |\n"
            f"| Status      | —               |\n"
        )

    def test_matches_pipeline_subtask(self):
        self.assertTrue(_is_pipeline_subtask(self._table("PIPELINE-SUBTASK")))

    def test_rejects_user_task(self):
        self.assertFalse(_is_pipeline_subtask(self._table("USER-TASK")))

    def test_rejects_user_subtask(self):
        self.assertFalse(_is_pipeline_subtask(self._table("USER-SUBTASK")))

    def test_tolerates_extra_spaces(self):
        content = "|  Task-type  |  PIPELINE-SUBTASK  |"
        self.assertTrue(_is_pipeline_subtask(content))

    def test_rejects_partial_match(self):
        # "PIPELINE-SUBTASK-EXTRA" should not match
        content = "| Task-type   | PIPELINE-SUBTASK-EXTRA |"
        self.assertFalse(_is_pipeline_subtask(content))

    def test_rejects_empty(self):
        self.assertFalse(_is_pipeline_subtask(""))

    def test_multiline_document(self):
        doc = (
            "# Task: build-1\n\n"
            "| Field       | Value           |\n"
            "|-------------|-----------------||\n"
            "| Task-type   | PIPELINE-SUBTASK |\n"
            "| Status      | —               |\n"
            "| Level       | TOP             |\n\n"
            "## Goal\n\nBuild something.\n"
        )
        self.assertTrue(_is_pipeline_subtask(doc))


# ---------------------------------------------------------------------------
# Level:TOP validation
# ---------------------------------------------------------------------------

class TestLevelPattern(unittest.TestCase):
    def _table(self, level: str) -> str:
        return (
            f"| Field       | Value           |\n"
            f"| Task-type   | PIPELINE-SUBTASK |\n"
            f"| Level       | {level}          |\n"
        )

    def test_matches_top(self):
        self.assertTrue(_is_level_top(self._table("TOP")))

    def test_rejects_internal(self):
        self.assertFalse(_is_level_top(self._table("INTERNAL")))

    def test_rejects_dash(self):
        self.assertFalse(_is_level_top(self._table("—")))

    def test_tolerates_extra_spaces(self):
        content = "|  Level  |  TOP  |"
        self.assertTrue(_is_level_top(content))

    def test_rejects_partial_match(self):
        content = "| Level       | TOPMOST |"
        self.assertFalse(_is_level_top(content))

    def test_rejects_empty(self):
        self.assertFalse(_is_level_top(""))

    def test_multiline_document(self):
        doc = (
            "# Task: build-1\n\n"
            "| Task-type   | PIPELINE-SUBTASK |\n"
            "| Level       | TOP             |\n\n"
            "## Goal\n\nBuild something.\n"
        )
        self.assertTrue(_is_level_top(doc))


# ---------------------------------------------------------------------------
# Combined: both checks on a realistic README
# ---------------------------------------------------------------------------

class TestCombinedValidation(unittest.TestCase):
    VALID_DOC = (
        "# Task: build-1\n\n"
        "| Field       | Value                   |\n"
        "|-------------|-------------------------|\n"
        "| Task-type   | PIPELINE-SUBTASK        |\n"
        "| Status      | —                       |\n"
        "| Level       | TOP                     |\n\n"
        "## Goal\n\nBuild a service.\n"
    )

    USER_TASK_DOC = (
        "# Task: user-service\n\n"
        "| Field       | Value     |\n"
        "| Task-type   | USER-TASK |\n"
        "| Status      | backlog   |\n\n"
        "## Goal\n\nOwner task.\n"
    )

    INTERNAL_DOC = (
        "# Task: handler\n\n"
        "| Task-type   | PIPELINE-SUBTASK |\n"
        "| Level       | INTERNAL         |\n\n"
        "## Goal\n\nA component.\n"
    )

    def test_valid_passes_both(self):
        self.assertTrue(_is_pipeline_subtask(self.VALID_DOC))
        self.assertTrue(_is_level_top(self.VALID_DOC))

    def test_user_task_fails_type_check(self):
        self.assertFalse(_is_pipeline_subtask(self.USER_TASK_DOC))

    def test_internal_passes_type_fails_level(self):
        self.assertTrue(_is_pipeline_subtask(self.INTERNAL_DOC))
        self.assertFalse(_is_level_top(self.INTERNAL_DOC))


if __name__ == "__main__":
    unittest.main()
