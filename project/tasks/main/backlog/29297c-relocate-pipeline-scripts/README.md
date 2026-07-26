# Task: relocate-pipeline-scripts

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | —               |
| Priority    | MED           |
| Category    | task-tooling           |
| Created     | 2026-07-26            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

Move the 7 hand-maintained **pipeline scripts** out of `project/tasks/scripts/`
(now 100% generator-owned) into a dedicated, non-generated home, so the two
owners' scripts don't cohabitate and a future regen can't clash with them.

## Context

Re-homed from create-project-system (its placeholder task 12), now that this
repo's tracker is live after the task-subsystem migration (PR #4).

After the migration, `project/tasks/scripts/` is emitted by create-project-system
on every `generate.sh` run. The 7 pipeline scripts still sit there,
hand-maintained: `advance-pipeline.sh`, `check-stop-after.sh`,
`new-pipeline-build.sh`, `new-pipeline-subtask.sh`, `on-task-complete.sh`,
`set-current-job.sh`, `pipeline-build-template.md`. Cohabitation is fragile — a
reader can't tell which files are safe to edit, and a `--force` regen or a
same-named generated script could clash.

Relocate the 7 to a dedicated dir (e.g. `project/pipeline/scripts/` or
`ai-builder/orchestrator/scripts/` — decide during execution), update every
caller (orchestrator, bootstrap, task READMEs), and confirm a re-run of
`generate.sh` is a **zero-diff regen** of `project/tasks/scripts/`.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
