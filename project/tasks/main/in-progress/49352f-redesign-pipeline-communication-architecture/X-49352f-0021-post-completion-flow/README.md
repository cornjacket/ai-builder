# Task: post-completion-flow

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 49352f-redesign-pipeline-communication-architecture             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Wire together the three post-completion steps — metrics (subtask 0011), README
rendering (subtask 0012), and master index rebuild (subtask 0013) — into an
ordered sequence that runs automatically after `HANDLER_ALL_DONE`. Also wire
the README render to re-run after each pipeline stage for live monitoring.

## Context

This is the integration subtask for the post-completion flow. Subtasks 0011,
0012, and 0013 each implement one piece independently; this subtask connects
them in the orchestrator in the correct order and with the correct triggers.

**Sequence on `HANDLER_ALL_DONE`:**
1. **Metrics** — write `run_summary` and `execution_log` to TOP-level `task.json`
   (subtask 0011)
2. **README render** — render TOP-level README and active task README from
   `task.json` (subtask 0012). Metrics must land first so the render includes
   the final run summary.
3. **Master index rebuild** — traverse the output directory tree and rebuild the
   combined documentation index (subtask 0013). README render runs first so the
   final README content is in place.

**Live monitoring (during run):**
After each pipeline stage the orchestrator calls the README render for the
TOP-level task and the currently active task. This gives a continuously updated
view of execution progress without waiting for completion.

**Dependency:** subtasks 0011, 0012, and 0013 must all be complete before this
subtask is implemented. This is why 0010 is last in the sequence.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
