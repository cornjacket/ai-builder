# Task: track-pipeline-build-metrics

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Next-subtask-id | 0012 |

## Goal

Instrument the orchestrator to capture and surface build metrics with zero
changes to agent prompts or behaviour. The orchestrator owns all monitoring;
agents are unaware. Design with a clean Python function boundary so metrics
can later be persisted to a database and surfaced in a dashboard.

### Architecture

- **`agent_wrapper.py`** — capture token counts from the `result` event
  emitted by the claude CLI after each invocation. Return them in `AgentResult`.
- **`metrics.py`** (new module) — pure functions called by the orchestrator:
  - `record_invocation(role, n, description, start, end, tokens, outcome)`
  - `update_task_doc(build_readme, invocations)` — live update after each agent
  - `write_run_summary(output_dir, run_data)` — called on `HANDLER_ALL_DONE`
  - `write_run_metrics_json(output_dir, run_data)` — called on `HANDLER_ALL_DONE`
- **`orchestrator.py`** — measure wall-clock start before `run_agent`, call
  `record_invocation` after each agent, call `update_task_doc` to write the
  live table, and call the write functions on `HANDLER_ALL_DONE`.

### Live execution log in the pipeline-subtask README

After every agent invocation the orchestrator rewrites the `## Execution Log`
section of the top-level pipeline-subtask README (the task with `Level: TOP`).
This gives a live progress view that can be monitored during a run.

Table format:
```
| # | Role | Description | Ended | Elapsed | Tokens In | Tokens Out | Tokens Cached |
```

`Description` is derived from the current job path
(e.g. `eab6f7-0001-handler` → `handler`).

The `## Execution Log` section is pre-populated with the header row by the
pipeline-subtask template so the orchestrator only needs to append rows.

### On `HANDLER_ALL_DONE`

Write to the output directory:
- `run-summary.md` — human-readable, with sections:
  1. Header (task, start, end, total wall-clock)
  2. Per-invocation table (same columns as live log)
  3. Per-role totals (role, count, total time, avg/invocation)
  4. Token usage by role (Tokens In, Tokens Out, Tokens Cached, Total) + grand total
  5. Decomposition tree (ASCII)
- `run-metrics.json` — machine-readable, same data, for cross-run aggregation

## Context

The first full end-to-end platform-monolith run (2026-03-16) produced enough
data to define what metrics are worth collecting. See Notes for the manual
summary from that run. The goal is to automate capture of these numbers so
every future pipeline run self-documents its performance characteristics.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [x] [X-51de6e-0000-update-agent-result-tokens](X-51de6e-0000-update-agent-result-tokens/)
- [x] [X-51de6e-0001-create-metrics-module](X-51de6e-0001-create-metrics-module/)
- [x] [X-51de6e-0002-update-orchestrator](X-51de6e-0002-update-orchestrator/)
- [x] [X-51de6e-0003-update-pipeline-templates](X-51de6e-0003-update-pipeline-templates/)
- [x] [X-51de6e-0004-smoke-test](X-51de6e-0004-smoke-test/)
- [x] [X-51de6e-0005-update-docs](X-51de6e-0005-update-docs/)
- [x] [X-51de6e-0006-document-monitoring-design](X-51de6e-0006-document-monitoring-design/)
- [x] [X-51de6e-0007-fix-elapsed-and-token-totals](X-51de6e-0007-fix-elapsed-and-token-totals/)
- [x] [X-51de6e-0008-dynamic-execution-log-insertion](X-51de6e-0008-dynamic-execution-log-insertion/)
- [x] [X-51de6e-0009-write-summary-to-readme](X-51de6e-0009-write-summary-to-readme/)
- [x] [X-51de6e-0011-implement-pipeline-build-script](X-51de6e-0011-implement-pipeline-build-script/)
<!-- subtask-list-end -->

## Notes

### Platform-monolith run — 2026-03-16

**Wall-clock time:** ~25 minutes (23:20:53 → 23:45:42)

**Role invocations (24 total):**

Elapsed time per invocation is approximated as the gap between consecutive execution log entries (orchestrator starts next invocation immediately after prior completion). ARCHITECT #1 start time is unknown (pipeline startup overhead not logged); its elapsed is omitted from the total.

| Role                  | #  | Invocation                       | Ended    | Elapsed |
|-----------------------|----|----------------------------------|----------|---------|
| ARCHITECT             | 1  | Decompose top-level              | 23:20:53 | —       |
| DECOMPOSE_HANDLER     | 1  | Create build-1 subtasks          | 23:22:35 | 1m 42s  |
| ARCHITECT             | 2  | Design metrics                   | 23:23:52 | 1m 17s  |
| IMPLEMENTOR           | 1  | Implement metrics                | 23:25:17 | 1m 25s  |
| TESTER                | 1  | Test metrics                     | 23:26:01 | 44s     |
| LEAF_COMPLETE_HANDLER | 1  | Advance to iam                   | 23:26:17 | 16s     |
| ARCHITECT             | 3  | Decompose iam                    | 23:27:37 | 1m 20s  |
| DECOMPOSE_HANDLER     | 2  | Create iam subtasks              | 23:28:59 | 1m 22s  |
| ARCHITECT             | 4  | Design auth-lifecycle            | 23:31:04 | 2m 05s  |
| IMPLEMENTOR           | 2  | Implement auth-lifecycle         | 23:32:35 | 1m 31s  |
| TESTER                | 2  | Test auth-lifecycle              | 23:33:11 | 36s     |
| LEAF_COMPLETE_HANDLER | 2  | Advance to authz-rbac            | 23:33:33 | 22s     |
| ARCHITECT             | 5  | Design authz-rbac                | 23:35:41 | 2m 08s  |
| IMPLEMENTOR           | 3  | Implement authz-rbac             | 23:37:04 | 1m 23s  |
| TESTER                | 3  | Test authz-rbac                  | 23:37:30 | 26s     |
| LEAF_COMPLETE_HANDLER | 3  | Advance to iam/integrate         | 23:37:48 | 18s     |
| ARCHITECT             | 6  | Design iam/integrate             | 23:40:07 | 2m 19s  |
| IMPLEMENTOR           | 4  | Implement iam/integrate          | 23:42:05 | 1m 58s  |
| TESTER                | 4  | Test iam/integrate               | 23:42:49 | 44s     |
| LEAF_COMPLETE_HANDLER | 4  | Advance to TOP integrate         | 23:43:04 | 15s     |
| ARCHITECT             | 7  | Design TOP integrate             | 23:44:11 | 1m 07s  |
| IMPLEMENTOR           | 5  | Implement TOP integrate          | 23:44:47 | 36s     |
| TESTER                | 5  | Test TOP integrate               | 23:45:25 | 38s     |
| LEAF_COMPLETE_HANDLER | 5  | DONE                             | 23:45:42 | 17s     |

**Per-role totals (measured):**

| Role                  | Count | Total time  | Avg/invocation |
|-----------------------|-------|-------------|----------------|
| ARCHITECT             | 7     | ~11m 36s ¹  | ~1m 39s        |
| DECOMPOSE_HANDLER     | 2     | 3m 04s      | 1m 32s         |
| IMPLEMENTOR           | 5     | 6m 53s      | 1m 23s         |
| TESTER                | 5     | 3m 08s      | 38s            |
| LEAF_COMPLETE_HANDLER | 5     | 1m 28s      | 18s            |

¹ Includes estimated ~1m30s for ARCHITECT #1 (start time not logged).

**Decomposition tree (3 pipeline levels):**

```
e50ab7-platform              (USER-TASK — Oracle boundary)
└── fa3480-build-1           (PIPELINE-SUBTASK, TOP)
    ├── 0bd07c-metrics        (atomic)
    ├── d5d551-iam            (decomposed)
    │   ├── 6c8e95-auth-lifecycle  (atomic)
    │   ├── 4b71a6-authz-rbac     (atomic)
    │   └── 9e7828-integrate      (atomic, INTERNAL)
    └── 09532b-integrate     (atomic, TOP)
```

**Implementations and test counts:**

| Component                   | Tests |
|-----------------------------|-------|
| internal/metrics            | 10    |
| internal/iam/authlifecycle  | 15    |
| internal/iam/authzrbac      | 15    |
| internal/iam (integrate)    | 15    |
| cmd/platform (integrate)    | 13    |
| **Total**                   | **68**|

Gold test result: **PASS** (all 5 HTTP endpoints verified).
