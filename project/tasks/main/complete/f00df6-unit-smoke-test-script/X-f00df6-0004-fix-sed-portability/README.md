# Task: fix-sed-portability

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | f00df6-unit-smoke-test-script             |
| Priority    | —           |
| Created     | 2026-04-02            |
| Completed | 2026-04-02 |
| Next-subtask-id | 0000               |

## Goal

Replace all `sed -i ''` calls across the task management scripts with a
cross-platform wrapper so the scripts run correctly on both macOS and Linux.

## Context

All scripts currently use BSD `sed -i ''` (macOS syntax). On Linux (GNU sed),
the correct form is `sed -i` with no empty string argument. This breaks the
bats tests — and the scripts themselves — on any Linux machine or CI runner.

**Fix:** add a `_sed_i()` helper to `task-json-helpers.sh` (already sourced by
most scripts) that detects the OS and calls the right form:

```bash
_sed_i() {
    if [[ "$(uname)" == "Darwin" ]]; then
        sed -i '' "$@"
    else
        sed -i "$@"
    fi
}
```

Then replace every `sed -i ''` occurrence across all scripts with `_sed_i`.

**Affected scripts (all use `sed -i ''`):**
- `move-task.sh`
- `complete-task.sh`
- `new-user-task.sh`
- `new-user-subtask.sh`
- `new-pipeline-subtask.sh`
- `new-pipeline-build.sh`
- `advance-pipeline.sh`
- `insert-subtask.sh`
- `rename-subtask.sh`
- `restore-task.sh`
- `delete-task.sh`
- `wont-do-subtask.sh`
- `task-id-helpers.sh`

Verify by running `bats tests/unit/shell/` after the fix — all 37 tests must
still pass on macOS. CI will verify Linux.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
