# Task: pipeline-subtask-template-machine-generated-notice

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | bc5c01-task-script-cleanup             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Add a machine-generated notice to the pipeline-subtask README template so
that anyone opening the file knows it is owned by the pipeline and should not
be hand-edited.

Add the notice as an HTML comment at the top of the template (invisible when
rendered but visible in a text editor):

```markdown
<!-- This file is managed by the ai-builder pipeline. Do not hand-edit. -->
```

Update both copies of the template:
- `project/tasks/scripts/pipeline-subtask-template.md`
- `target/project/tasks/scripts/pipeline-subtask-template.md`

## Context

Pipeline-subtask READMEs are created and updated by orchestrator agents
(`new-pipeline-subtask.sh`, `on-task-complete.sh`, etc.). Hand-editing them
can corrupt the metadata fields the pipeline depends on. A visible notice in
the raw file prevents accidental edits.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
