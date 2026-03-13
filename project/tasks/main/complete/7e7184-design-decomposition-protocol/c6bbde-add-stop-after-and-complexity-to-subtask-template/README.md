# Subtask: add-stop-after-and-complexity-to-subtask-template

| Field    | Value                |
|----------|----------------------|
| Status | complete |
| Epic     | main             |
| Tags     | —             |
| Parent   | 7e7184-design-decomposition-protocol           |
| Priority | —         |

## Description

Add `Stop-after` and `Complexity` metadata fields to the subtask README
template used by `new-task.sh`.

`Stop-after` marks a phase boundary — when true, the Oracle pauses after the
subtask completes and presents results to the human.

| Field | Default | Values |
|-------|---------|--------|
| `Stop-after` | `false` | `true` / `false` |
| `Complexity` | — | `atomic` / `composite` |

`Complexity: atomic` means the subtask can go directly to the IMPLEMENTOR.
`Complexity: composite` means it requires a decomposition pass first.

Deliverables:
1. Find the subtask template file used by `new-task.sh` (likely in
   `project/tasks/scripts/` or `target/project/tasks/`)
2. Add both fields to the template metadata table with correct defaults
3. Update `target/project/tasks/README.md` to document both fields
4. Verify `new-task.sh` creates subtasks using the updated template

Source: "The Stop-after Flag" and "Deterministic vs. Non-Deterministic
Elements" sections of `sandbox/brainstorm-oracle-and-n-phase-pipeline.md`,
and brainstorm open question #5.

## Notes

Resolving this subtask closes brainstorm open question #5.
