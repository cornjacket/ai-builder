# Task: port-regression-task-json

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

Before running the regression, update the sandbox regression build task.json
files to include `"goal"` and `"context"` fields. The orchestrator no longer
falls back to README parsing — a missing `goal` field is a hard error.

## Context

`49352f-0000` added `goal`/`context` fields to `task.json` and removed the
README fallback. Any existing regression build task created before that change
will be missing these fields and will cause the orchestrator to error:
`'goal' field missing from task.json`.

**Changes required:**

For each sandbox regression build task.json (platform-monolith, user-service,
etc.), add `"goal"` and `"context"` string fields matching the content of the
corresponding `## Goal` and `## Context` sections in the README. The reset
script creates fresh builds via `new-pipeline-build.sh`, which now writes
these fields automatically — so this is a one-time migration for any builds
that predate 49352f-0000.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
