# Task: incremental-subtask-ids

| Field       | Value                       |
|-------------|-----------------------------|
| Task-type   | USER-TASK                   |
| Status | complete |
| Epic        | main                        |
| Tags        | task-management, scripts    |
| Priority    | HIGH                        |
| Next-subtask-id | 0010 |

## Goal

Replace random-hash subtask directory names with deterministic incremental
IDs, and mark completed subtasks visually with an `X-` prefix so the task
tree is human-readable at a glance.

**New naming convention:**

- Every task/subtask README gains a `Next-subtask-id: 0000` metadata field
- When a new subtask is created under parent `a1b2c3-foo`, it gets the
  directory name `a1b2c3-0000-subtask-name`, `a1b2c3-0001-subtask-name`, etc.
- `Next-subtask-id` in the parent is incremented by one after each creation
- When a subtask is marked complete, its directory is renamed with an `X-`
  prefix: `X-a1b2c3-0000-subtask-name`

**Result:** a task tree like:

```
c98d7b-incremental-subtask-ids/
    X-c98d7b-0000-design-id-scheme/
    X-c98d7b-0001-update-templates/
    c98d7b-0002-update-new-subtask-scripts/
    c98d7b-0003-update-complete-script/
    c98d7b-0004-update-supporting-scripts/
    c98d7b-0005-update-target-scripts/
    c98d7b-0006-update-documentation/
    c98d7b-0007-smoke-test/
```

## Context

The current system prefixes subtask directories with a random 6-char hex
hash (e.g. `d05f90-split-task-manager-into-handlers`). This makes it
impossible to tell ordering, progress, or hierarchy from directory names
alone. The change is purely additive to the metadata schema and replaces
the hash-generation logic in subtask creation scripts.

Top-level tasks (USER-TASKs created with `new-user-task.sh`) keep their
random hash prefix — they have no parent to inherit an ID from. Only
subtasks switch to the incremental scheme.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [x] [052976-design-id-scheme](052976-design-id-scheme/)
- [x] [1a5227-update-templates](1a5227-update-templates/)
- [x] [d15085-update-new-subtask-scripts](d15085-update-new-subtask-scripts/)
- [x] [X-ef6e1e-update-complete-script](X-ef6e1e-update-complete-script/)
- [x] [X-feb2df-update-supporting-scripts](X-feb2df-update-supporting-scripts/)
- [x] [X-d2ec46-update-target-scripts](X-d2ec46-update-target-scripts/)
- [x] [X-d985cd-update-documentation](X-d985cd-update-documentation/)
- [x] [X-8c5e30-smoke-test](X-8c5e30-smoke-test/)
- [x] [X-8087e2-migrate-existing-subtask-ids](X-8087e2-migrate-existing-subtask-ids/)
<!-- subtask-list-end -->

## Notes

_None._
