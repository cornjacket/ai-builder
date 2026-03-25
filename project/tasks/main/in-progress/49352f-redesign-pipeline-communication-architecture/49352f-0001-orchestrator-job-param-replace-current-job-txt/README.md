# Task: orchestrator-job-param-replace-current-job-txt

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status      | —                      |
| Epic        | main               |
| Tags        | —               |
| Parent      | 49352f-redesign-pipeline-communication-architecture             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Replace `current-job.txt` with a `--job path/to/task.json` CLI parameter.
Replace the `set-current-job.sh` Oracle workflow step with a direct path
argument. The orchestrator tracks the active task path in memory; writes
`last-job.json` as the resume artifact instead of `current-job.txt`.

## Context

`current-job.txt` is program state persisted to a file unnecessarily. It is
an indirect input — the orchestrator reads the active task path from a file on
disk rather than receiving it directly. If the file is missing, stale, or wrong
the pipeline silently misbehaves. `set-current-job.sh` is an extra manual step
the Oracle must run before every launch.

**Changes required:**

1. **`orchestrator.py`** — add `--job` CLI parameter accepting the path to the
   TOP-level `task.json`. Remove `current-job.txt` read at startup. Track the
   active task path in memory (updated by DECOMPOSE_HANDLER and
   LEAF_COMPLETE_HANDLER as the pipeline advances). Write `last-job.json` to
   the output directory after each stage.

2. **`--resume`** — reads `last-job.json` from the output directory to restore
   the active task path. `last-job.json` is a resume artifact, not an input.

3. **`set-current-job.sh`** — eliminated. Pipeline launch becomes:
   ```bash
   python3 orchestrator.py --job path/to/build-1/task.json
   ```

4. **Documentation** — update `README.md` and any Oracle workflow docs to
   reflect the new launch command.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
