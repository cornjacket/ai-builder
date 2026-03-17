# Task: implement-advance-pipeline-script

| Field       | Value                        |
|-------------|------------------------------|
| Task-type   | USER-SUBTASK                 |
| Status | complete |
| Epic        | main                         |
| Tags        | orchestrator, tm             |
| Parent      | 0838a5-tm-tree-traversal     |
| Priority    | —                            |

## Goal

Implement `advance-pipeline.sh` — a script that encapsulates the full upward
tree-traversal logic after a leaf task completes, returning either the next
task path or a DONE signal.

## Context

The traversal algorithm after a leaf completes:

```
current = completed leaf README path

loop:
    if current.Last-task == false:
        next = next-subtask.sh(parent_dir)
        set-current-job(next)
        print "NEXT <path>"
        exit 0

    else:  # last at this level — walk up
        parent_readme = dirname(dirname(current))/README.md

        if parent_readme.Task-type is USER-TASK or USER-SUBTASK:
            # Crossed the human/pipeline boundary — pipeline tree complete
            complete pipeline root task
            print "DONE"
            exit 0

        # Mark composite parent complete
        grandparent_dir = dirname(dirname(parent_readme))
        complete-task.sh --parent grandparent_dir --name parent_id

        current = parent_readme
        continue  # walk up another level
```

The "are we at root" check is: walk up until the parent README has
`Task-type: USER-TASK` or `USER-SUBTASK` — that is the human/pipeline boundary.
No special flag needed.

**Interface:**
```bash
advance-pipeline.sh --current <readme-path> --output-dir <dir> --epic <epic>
# stdout: "NEXT <path>" or "DONE"
# exit 0 always (errors exit non-zero)
```

Also implement supporting scripts the TM calls directly:

- **`is-top-level.sh <readme>`** — exit 0 if `Level: TOP`, exit 1 if `INTERNAL`.
  Formalizes the Level check so the TM doesn't parse markdown.
- **`check-stop-after.sh <readme>`** — exit 0 if `Stop-after: true`, exit 1 otherwise.
  Same rationale — deterministic field read, not prose instruction.
- **`on-task-complete.sh --current <readme> --output-dir <dir> --epic <epic>`** —
  wraps `complete-task.sh` + `check-stop-after.sh` + `advance-pipeline.sh` into
  a single call. Returns `STOP_AFTER | NEXT <path> | DONE`. Reduces the
  TESTER_TESTS_PASS branch to one script call and an outcome emit.

**Important constraint:** these scripts are called by the TM *agent* — they are
not integrated into the orchestrator itself. The orchestrator must remain agnostic
of the task management system. See brainstorm for rationale.

Deployed to both `project/tasks/scripts/` and `target/project/tasks/scripts/`.

## Subtasks

<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
