# Task: update-templates

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 829461-split-task-format-md-json-and-scripts             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Update regression test reset.sh files to use the new prose-only pipeline
task README format and read Level/Status from task.json instead of README.

## Context

After subtasks 0001-0003, pipeline subtask READMEs are prose-only (no
metadata table). Structured metadata is in task.json.

The TM regression reset.sh files (platform-monolith, user-service) have
two problems:
1. The inline template still contains the old metadata table (Task-type,
   Level, Complexity, Stop-after, Last-task, Status, etc.). Since the
   orchestrator now reads from task.json (created by new-pipeline-build.sh),
   the table is harmless noise — but misleading and should be removed.
2. platform-monolith/reset.sh guard reads Level and Status from README
   with grep to detect an in-progress pipeline. These fields are now in
   task.json. The guard needs to read from task.json instead.

The user-service reset.sh also lacks the ## Test Command section that
the ARCHITECT now fills in.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
