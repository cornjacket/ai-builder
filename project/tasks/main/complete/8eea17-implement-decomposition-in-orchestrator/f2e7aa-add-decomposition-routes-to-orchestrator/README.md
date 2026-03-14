# Subtask: add-decomposition-routes-to-orchestrator

| Field    | Value                |
|----------|----------------------|
| Status | complete |
| Epic     | main             |
| Tags     | —             |
| Parent   | 8eea17-implement-decomposition-in-orchestrator           |
| Priority | —         |

## Description

Add decomposition outcomes to the `ROUTES` table in `orchestrator.py`.

Entries to add (using final outcome names from `d3616d-rename-pipeline-outcomes-for-clarity`):

```python
("ARCHITECT",    "COMPONENTS_READY"): "TASK_MANAGER",
("ARCHITECT",    "COMPONENT_READY"):  "IMPLEMENTOR",
("ARCHITECT",    "NEEDS_REVISION"):   "ARCHITECT",    # self-loop — requires iteration limit (0be578)
("TASK_MANAGER", "STOP_AFTER"):       None,
```

Also update `IMPLEMENTOR` and `TESTER` route keys if `d3616d` has already
renamed `DONE` → `IMPLEMENTATION_DONE` and `DONE`/`FAILED` → `TESTS_PASS`/`TESTS_FAIL`.

**Gated by:** `d3616d-rename-pipeline-outcomes-for-clarity`

## Notes

The `NEEDS_REVISION` self-loop is safe only after `0be578-add-role-iteration-limit`
is also implemented. Both should land together.
