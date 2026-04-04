# tests/regression/lib

Shared shell libraries for regression recording and replay scripts.

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
