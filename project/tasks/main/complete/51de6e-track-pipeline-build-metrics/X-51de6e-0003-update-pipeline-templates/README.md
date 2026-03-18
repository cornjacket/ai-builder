# Task: update-pipeline-templates

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

Add a `## Execution Log` section to all four pipeline-subtask templates so the
orchestrator has a stable location to write the live invocation table.

Files to update:
- `project/tasks/scripts/pipeline-build-template.md`
- `target/project/tasks/scripts/pipeline-build-template.md`

Add at the end of the file, after `## Notes`:

```markdown
## Execution Log

| # | Role | Agent | Description | Ended | Elapsed | Tokens In | Tokens Out | Tokens Cached |
|---|------|-------|-------------|-------|---------|-----------|------------|---------------|
```

The orchestrator will append rows to this table after each agent invocation.
The header row must be present for `metrics.update_task_doc` to locate the
section — it uses the `## Execution Log` heading as an anchor.

## Context

Only pipeline-subtask templates need this section — user-tasks and
user-subtasks are not execution targets. The two templates (source and target)
must stay in sync.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
