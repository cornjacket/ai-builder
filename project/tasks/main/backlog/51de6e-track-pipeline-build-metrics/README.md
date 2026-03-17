# Task: track-pipeline-build-metrics

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |

## Goal

Instrument the orchestrator pipeline to record build metrics per run and write
them to the output directory alongside the execution log. Metrics to capture:

- **Wall-clock time:** total run time, and elapsed time per role invocation
- **Role invocations:** count per role, and a per-invocation log with role,
  task name, elapsed time, and outcome
- **Token usage:** total tokens (input + output + cache), and per-role
  breakdown — useful for cost attribution and identifying expensive roles
- **Components:** number of modules implemented, decomposition depth, test counts

When LEAF_COMPLETE_HANDLER fires `HANDLER_ALL_DONE`, the orchestrator must
write a human-readable `run-summary.md` to the output directory. The summary
must include:

1. **Header** — task name, start time, end time, total wall-clock time
2. **Per-invocation table** — one row per role invocation in order:
   role, invocation #, description (task being worked), end time, elapsed
3. **Per-role totals table** — role, count, total time, avg time/invocation
4. **Token usage table** — role, input tokens, output tokens, cache tokens,
   total; with a grand-total row
5. **Decomposition tree** — ASCII representation of the pipeline-subtask
   hierarchy built during the run
6. **Implementations table** — component path, test count

A machine-readable `run-metrics.json` should also be written with the same
data for aggregation across runs.

## Context

The first full end-to-end platform-monolith run (2026-03-16) produced enough
data to define what metrics are worth collecting. See Notes for the manual
summary from that run. The goal is to automate capture of these numbers so
every future pipeline run self-documents its performance characteristics.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
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
