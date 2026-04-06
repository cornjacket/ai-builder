# Task: abstract-record-replay-scripts

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | ccf4a4-establish-regression-recordings             |
| Priority    | —           |
| Created     | 2026-04-04             |
| Completed | 2026-04-04 |
| Next-subtask-id | 0000               |

## Goal

Extract the shared logic from `record.sh` and `test-replay.sh` into a
common library (`tests/regression/lib/record-lib.sh`) so each regression's
scripts are reduced to setting a handful of variables and sourcing the lib.

## Context

`record.sh` and `test-replay.sh` are nearly identical across regressions —
only these values differ per test:

- `RECORD_DIR` / `TARGET_REPO` / `OUTPUT_DIR` (sandbox paths)
- `BRANCH` (recording branch name = test name)
- `TOP_TASK_DIR` (path inside target repo used for snapshot exclusion)
- `STATE_MACHINE` (builder vs doc machine)

Everything else — the guard logic, `.git` wipe, fetch-from-remote, routing
verification, snapshot comparison, push sequence — is duplicated verbatim.

**Proposed structure:**

```
tests/regression/lib/
    record-lib.sh      — common record.sh logic; caller sets variables then sources
    replay-lib.sh      — common test-replay.sh logic; caller sets variables then sources
```

Each test's `record.sh` becomes:

```bash
RECORD_DIR="..."
BRANCH="..."
STATE_MACHINE="..."
source "$(dirname "$0")/../../lib/record-lib.sh"
```

**Also update** `platform-monolith/record.sh` and `platform-monolith/test-replay.sh`
(already written) to use the lib once it exists, so they serve as the
reference implementation for subsequent tests.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
