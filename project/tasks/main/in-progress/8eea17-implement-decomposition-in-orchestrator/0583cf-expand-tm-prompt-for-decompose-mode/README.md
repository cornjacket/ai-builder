# Subtask: expand-tm-prompt-for-decompose-mode

| Field    | Value                |
|----------|----------------------|
| Status | complete |
| Epic     | main             |
| Tags     | —             |
| Parent   | 8eea17-implement-decomposition-in-orchestrator           |
| Priority | —         |

## Description

Expand the TASK_MANAGER prompt in `orchestrator.py` to handle decompose mode:
when the previous role was ARCHITECT and outcome was `COMPONENTS_READY`.

TM instructions for this case:
1. Read the component table from the ARCHITECT's output (format defined in
   `ai-builder/orchestrator/decomposition.md`)
2. For each row, create a subtask using `new-task.sh` with the `Complexity`
   field set
3. Order subtasks by implementation priority
4. Set the first atomic subtask as the next job: write a `JOB-component-design`
   document and write its path to `current-job.txt`
5. Output `JOBS_READY`

If the first subtask is `Complexity: composite`, TM writes a `JOB-service-build`
document instead and the pipeline recurses into another decompose pass.

## Notes

Depends on `47412e-create-decomposition-job-templates` — TM needs the
templates to exist before it can write job documents.
