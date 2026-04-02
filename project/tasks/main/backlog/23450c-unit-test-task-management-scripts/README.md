# Task: unit-test-task-management-scripts

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | —               |
| Priority    | MED           |
| Created     | 2026-04-02            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

Add a unit test suite for the task management shell scripts and shared helpers,
covering the core create/complete/move lifecycle and key edge cases.

## Context

The task management scripts (`new-user-task.sh`, `new-user-subtask.sh`,
`new-pipeline-subtask.sh`, `complete-task.sh`, `move-task.sh`, etc.) have no
automated tests. Correctness has been validated through use, but bugs have
surfaced (e.g. the `sed` delimiter bug in `new-user-subtask.sh`, missing
`Task-type` field in `reset.sh`). A test suite would catch regressions when
scripts are modified.

Existing unit tests live in `tests/unit/` (Python). Task script tests should
live there too, using a temporary directory as the repo root so tests are
fully isolated and leave no side effects.

**Scope — scripts to cover:**
- `new-user-task.sh` — creates directory, README with correct fields (including Created), registers in status README
- `new-user-subtask.sh` — increments Next-subtask-id, correct NNNN naming, parent with `/` in path
- `new-pipeline-subtask.sh` — creates task.json with correct fields (including created_at), prose README
- `complete-task.sh` — top-level task moves to complete/, sets Completed date; subtask sets [x] + Status; pipeline subtask sets completed_at in task.json; --undo reverses each
- `move-task.sh` — directory moves, status README updated correctly

**Out of scope:** `list-tasks.sh`, `show-task.sh`, `delete-task.sh`, `restore-task.sh` — lower risk, lower value.

## Notes

Tests should create a minimal repo skeleton (epic/status dirs + seed README)
in a `tempfile.mkdtemp()` directory and invoke scripts via `subprocess.run()`
with `REPO_ROOT` overridden. No mocking of filesystem operations.
