# Task: update-orchestrator

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 51de6e-track-pipeline-build-metrics             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Wire `metrics.py` into `orchestrator.py` so every invocation is recorded and
the live execution log is updated after each agent completes.

Changes to `orchestrator.py`:
1. Import `metrics` and maintain `invocations: list[InvocationRecord] = []`
   and `role_counters: dict[str, int] = {}` in the main loop.
2. Record `start = datetime.now()` before each `run_agent` call.
3. After each `run_agent`, call `metrics.record_invocation(role, agent, ...)`
   — `agent` is `AGENTS[current_role]` (already available). Append to
   `invocations`. Increment `role_counters[role]`.
4. Track `build_readme: Path | None`. Set it when `job_doc` changes to a
   README containing `| Level | TOP |` (checked after each HANDLER_SUBTASKS_READY
   and also on the initial job_doc if it has Level: TOP).
5. After each invocation, if `build_readme` is set, call
   `metrics.update_task_doc(build_readme, invocations)`.
6. On `HANDLER_ALL_DONE`, call `metrics.write_run_summary(OUTPUT_DIR, ...)`
   and `metrics.write_run_metrics_json(OUTPUT_DIR, ...)`.

`description` for each invocation: extract from `job_doc` path — take the last
directory segment and strip the leading `{id}-{NNNN}-` or `{id}-` prefix to
get the human-readable name (e.g. `51de6e-0001-handler` → `handler`).

## Context

The orchestrator is the only component that knows wall-clock time and job
context. Agents must remain unaware of monitoring. The Level: TOP check avoids
hardcoding any task name — the orchestrator discovers the build README at runtime.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
