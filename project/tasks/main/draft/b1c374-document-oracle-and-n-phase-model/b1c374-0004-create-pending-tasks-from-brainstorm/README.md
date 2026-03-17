# Subtask: create-pending-tasks-from-brainstorm

| Field    | Value                |
|----------|----------------------|
| Status   | —                    |
| Epic     | main             |
| Tags     | —             |
| Parent   | b1c374-document-oracle-and-n-phase-model           |
| Priority | —         |

## Description

Create tasks for items in the "Pending Tasks to Create" section of
`sandbox/brainstorm-oracle-and-n-phase-pipeline.md`, then delete the
brainstorm once all content is confirmed absorbed.

Tasks to create (check for existing task before creating each):
- Design `project/reviews/` structure and format
- Add `project/reviews/` to `target/` skeleton and `setup-project.sh`
- Design planning tools available to ARCHITECT in Planning mode
- Add `--mode` or equivalent to orchestrator, or formalise job doc intent field

Tasks already covered (skip):
- `roles/ORACLE.md` → tracked as `311b40-create-roles-oracle-md`
- Planning-mode outcomes (`PLAN_READY`, `NEEDS_REVISION`) → tracked in
  `7e7184-design-decomposition-protocol`

After all content from the brainstorm is confirmed captured in documentation
or tasks, delete `sandbox/brainstorm-oracle-and-n-phase-pipeline.md`.

## Notes

This is the last subtask — do not run it until all other subtasks in this
task are complete and the brainstorm content is verified as fully absorbed.
