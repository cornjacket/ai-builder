# Task: project-pipeline-token-and-time-cost

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Use existing regression run metrics to build a projection model: given a
pipeline job, estimate total token consumption and wall-clock duration before
the run starts.

## Context

The orchestrator writes `run-metrics.json` after each run with per-role token
counts and timing. The regression suite has two completed doc-pipeline runs
(`doc-user-service`, `doc-platform-monolith`) with known source tree sizes.

**Workflow:**
1. Collect `run-metrics.json` from both completed regression runs.
2. Extract: tokens per role invocation, elapsed time per role invocation,
   number of source files and directories per run.
3. Derive per-unit cost estimates:
   - tokens per atomic leaf (DOC_ARCHITECT atomic + POST_DOC_HANDLER + LCH)
   - tokens per composite node (DOC_INTEGRATOR + POST_DOC_HANDLER + LCH)
   - tokens per DECOMPOSE_HANDLER call
   - wall-clock seconds per role (average + p90)
4. Given a new source tree, count leaves and composite nodes → multiply by
   per-unit estimates → produce a projected token total and elapsed time range.
5. Document the model and its assumptions. Identify the dominant cost drivers.

**Depends on:** `74d718-research-claude-token-availability` — the projection
model is only useful for scheduling if we can compare it against available
quota.

Output: `sandbox/research-pipeline-cost-model.md` with the data, model, and
per-run projection formula.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
