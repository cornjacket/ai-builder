# Task: audit-task-and-readme-references

| Field    | Value                                        |
|----------|----------------------------------------------|
| Status   | draft                                        |
| Epic     | main                                         |
| Tags     | documentation                                |
| Parent   | f1b8a0-establish-ai-builder-documentation    |
| Priority | MED                                          |

## Description

Review all task READMEs and component READMEs in the repo to ensure they
reference official checked-in documentation rather than sandbox brainstorm files.

Steps:
- Search for any references to `sandbox/` in task READMEs, CLAUDE.md,
  and component READMEs
- Replace each reference with a pointer to the corresponding official doc
  created in `create-docs-from-brainstorms`
- Where no official doc exists yet for a referenced topic, flag it so a
  doc can be added

## Documentation

None needed — this is a cleanup task.

## Subtasks

<!-- When a subtask is finished, run complete-subtask.sh to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

Depends on `create-docs-from-brainstorms` being complete first.
