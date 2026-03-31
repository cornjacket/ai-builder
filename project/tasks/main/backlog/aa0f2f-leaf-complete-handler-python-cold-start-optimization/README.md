# Task: leaf-complete-handler-python-cold-start-optimization

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Reduce LEAF_COMPLETE_HANDLER wall-clock time from ~14 s to under 2 s by
eliminating redundant Python3 process spawns during task completion. Each
JSON helper in `task-json-helpers.sh` launches an independent Python3
process; a single LCH invocation chains 4–6 of these, causing significant
cold-start stacking on the first invocation of a pipeline run.

## Context

Observed in the user-service regression run (`sandbox/user-service-target`,
task `86a08c-user-service`, build `86a08c-0000-build-1`). Execution log entry:

```
| 8 | LEAF_COMPLETE_HANDLER | internal | store | HANDLER_SUBTASKS_READY | 14s | 0 | 0 | 0 |
```

The `store` LCH took 14 s while the `handlers` LCH (entry 14) took only 1 s.
The difference is the OS page-cache warm-up effect: `store` is the first
Python3 invocation of the run, so the interpreter, stdlib `.pyc` files, and
site-packages are all loaded cold from disk. By the time `handlers` runs,
Python is hot in the page cache.

### Root cause

`task-json-helpers.sh` implements every JSON operation as a separate Python3
heredoc invocation:

```bash
json_complete_subtask  → python3 -   (spawn #1)
json_set_str           → python3 -   (spawn #2)
json_get               → python3 -   (spawn #3, inside advance-pipeline.sh)
json_next_subtask      → python3 -   (spawn #4, inside next-subtask.sh)
```

On macOS each cold Python3 start costs ~2–3 s. Five spawns × 2.5 s ≈ 14 s.

### Proposed fix

Consolidate into a single `task-json-ops.py` script (or equivalent) that
accepts a subcommand and handles all operations in one process. Alternatively,
batch the two writes in `complete-task.sh` (mark-complete + set-status) into
a single Python call. Either approach reduces 5–6 spawns to 1–2 per LCH,
eliminating cold-start stacking and bringing total LCH time under 2 s even
on a cold cache.

The fix must be applied to both `project/tasks/scripts/task-json-helpers.sh`
and `target/project/tasks/scripts/task-json-helpers.sh`.

## Notes

Low urgency — affects wall-clock time only, not correctness. Priority can be
raised if pipeline run times become a bottleneck.
