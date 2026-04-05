# tests/regression/lib

Shared shell libraries and utilities for regression recording, replay, and history management.

## record-lib.sh

Sourced by each test's `record.sh`. Handles the full recording lifecycle:
guards against accidental re-records, wipes prior recording history, resets
the workspace, runs the orchestrator with `--record-to`, and pushes to the
`ai-builder-recordings` remote.

**Caller must set before sourcing:**

| Variable | Description |
|---|---|
| `DIR` | Absolute path to the test directory (for `reset.sh`) |
| `REPO_ROOT` | Absolute path to the repo root |
| `RECORD_DIR` | Sandbox directory for recording output |
| `BRANCH` | Recording branch name in `ai-builder-recordings` |
| `STATE_MACHINE` | Path to the orchestrator state machine JSON |
| `FORCE` | `0` (default) or `1` (allow overwriting existing recording) |
| `REMOTE_URL` | _(optional)_ defaults to `cornjacket/ai-builder-recordings` |

## replay-lib.sh

Sourced by each test's `test-replay.sh`. Handles the full replay verification:
fetches recording from remote if absent, resets workspace with pinned task ID,
replays without AI calls, verifies routing path, and compares output snapshot.

**Caller must set before sourcing:**

| Variable | Description |
|---|---|
| `DIR` | Absolute path to the test directory (for `reset.sh`) |
| `REPO_ROOT` | Absolute path to the repo root |
| `RECORD_DIR` | Sandbox directory containing the recording |
| `BRANCH` | Recording branch name in `ai-builder-recordings` |
| `STATE_MACHINE` | Path to the orchestrator state machine JSON |
| `TOP_TASK_NAME` | Task name suffix in target repo path (e.g. `user-service`, `platform`) |
| `REMOTE_URL` | _(optional)_ defaults to `cornjacket/ai-builder-recordings` |

## archive-run.sh

Archives the completed pipeline run to a timestamped `runs/` directory
immediately after the orchestrator exits. Copies `execution.log`, `task.json`,
and `README.md` from the Level:TOP task, appends a summary row to
`run-history.md`, and updates the `last_run` symlink.

Called by `reset.sh` (to archive the previous run before wiping) and by
`run.sh` and `record-lib.sh` (immediately after the orchestrator exits,
eliminating the one-run lag).

If no `execution.log` exists in `--output-dir`, exits 0 silently.

**Usage:**

```bash
bash tests/regression/lib/archive-run.sh \
    --target-repo <path> \
    --output-dir  <path> \
    --runs-dir    <path> \
    --format      builder|doc
```

| Flag | Description |
|---|---|
| `--target-repo` | Sandbox target repo (where Level:TOP task.json lives) |
| `--output-dir` | Orchestrator output dir (execution.log lives here) |
| `--runs-dir` | Regression's `runs/` directory |
| `--format` | `builder` (ARCHITECT/IMPLEMENTOR/TESTER) or `doc` (ARCHITECT/IMPLEMENTOR) |

## update-run-history.sh

Token-free script that fills in the **Gold** and **Notes** columns on the last
data row of a `run-history.md` file. `reset.sh` appends rows automatically with
token counts and timing, but leaves Gold and Notes blank. Call this script after
gold tests complete.

**Usage:**

```bash
bash tests/regression/lib/update-run-history.sh \
    --history tests/regression/<name>/runs/run-history.md \
    --gold    pass|fail \
    --notes   "<triggering-task-or-reason>"
```

| Flag | Description |
|---|---|
| `--history` | Path to the `run-history.md` file |
| `--gold` | `pass` or `fail` |
| `--notes` | Triggering user task name, or a brief reason (e.g. `routine health check`) |

## add-to-recordings-readme.sh

Adds a new row to the Regression tests table in the ai-builder-recordings
main branch README.md. Run once when a regression's recording is pushed for
the first time. Re-records do not require a README update.

**Usage:**

```bash
bash tests/regression/lib/add-to-recordings-readme.sh \
    --name        <test-name> \
    --description "<what this regression exercises>"
```

| Flag | Description |
|---|---|
| `--name` | Branch name in `ai-builder-recordings` (matches `tests/regression/<name>/`) |
| `--description` | One-line description of what the test exercises |
