"""Shared pytest fixtures for ai-builder unit tests."""

import json
import sys
import tempfile
from pathlib import Path

import pytest

# Put the orchestrator package on the path for all tests in this directory.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "ai-builder" / "orchestrator"))


@pytest.fixture
def tmp_task_dir(tmp_path):
    """Return a tmp_path with a minimal task directory tree.

    Layout:
        <tmp_path>/
            project/tasks/main/
                draft/
                backlog/
                in-progress/
                complete/
    """
    for folder in ("draft", "backlog", "in-progress", "complete"):
        (tmp_path / "project" / "tasks" / "main" / folder).mkdir(parents=True)
    return tmp_path


@pytest.fixture
def mock_task_json(tmp_path):
    """Return a factory that writes a task.json to a temp dir and returns its Path.

    Usage:
        path = mock_task_json({"level": "TOP", "name": "my-task"})
    """
    def _make(data: dict, subdir: str = "") -> Path:
        d = tmp_path / subdir if subdir else tmp_path
        d.mkdir(parents=True, exist_ok=True)
        task_json = d / "task.json"
        defaults = {
            "name": "test-task",
            "level": "",
            "status": "in-progress",
            "goal": "Test goal.",
            "context": "",
            "subtasks": [],
        }
        defaults.update(data)
        task_json.write_text(json.dumps(defaults, indent=2) + "\n")
        return task_json

    return _make
