# Task: pipeline-loop-detection

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

Detect pipeline loops by tracking (role, description) pairs across invocations
and halting with a clear error when the same pair repeats consecutively.

## Context

Observed during platform-monolith regression: ARCHITECT(iam) →
DECOMPOSE_HANDLER(iam) repeated indefinitely because DECOMPOSE_HANDLER was
pointing current-job.txt back at the iam README rather than advancing to the
first child. MAX_ROLE_ITERATIONS didn't catch it because the role alternated
between ARCHITECT and DECOMPOSE_HANDLER, resetting the counter each time.

**Detection approach:** after each invocation, compare (role, description) with
the previous invocation. If the same pair appears consecutively — or within a
small sliding window — halt with a clear error message identifying the loop.

Example error:
```
[orchestrator] ERROR: pipeline loop detected — ARCHITECT/iam repeated
consecutively (iteration 2). This indicates DECOMPOSE_HANDLER is not
advancing current-job.txt to a child task. Halting.
```

A consecutive repeat of (role, description) should never happen in a healthy
pipeline: DECOMPOSE_HANDLER always advances to a child, LCH advances to the
next sibling or parent. Any repeat signals a broken advance.

**Stronger check — current-job.txt value:** same role + same `current-job.txt`
value between consecutive invocations is a definitive loop. The file's value
must change on every handler advance. This check catches loops even when the
description string is ambiguous (e.g. two sibling components with the same
name at different levels).

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
