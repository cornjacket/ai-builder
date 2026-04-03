# Task: store-hex-id-in-manifest

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status      | —                      |
| Epic        | main               |
| Tags        | —               |
| Parent      | 4603fa-pipeline-record-replay             |
| Priority    | —           |
| Created     | 2026-04-03            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

Store the top-level user task hex ID in `recording.json` so replay tooling
can reproduce exact task directory names. Add a `task_hex_id` field to the
manifest. Update `recorder.write_manifest()` to accept `task_hex_id: str | None = None`
and write it when provided. In `orchestrator.py`, extract the hex ID from
`initial_job_doc` at record time: the user-task directory is two levels above
the build README (`initial_job_doc.parent.parent`), and the hex ID is the
portion before the first `-` in its name.

## Context

All subtask hex prefixes derive from the top-level user task ID, so pinning
one value reproduces the full path structure. The manifest field sits at the
top level alongside `recorded_at` and `ai_builder_commit`.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
