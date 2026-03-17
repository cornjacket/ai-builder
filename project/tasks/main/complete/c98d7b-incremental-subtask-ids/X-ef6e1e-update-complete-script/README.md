# Task: update-complete-script

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | c98d7b-incremental-subtask-ids             |
| Priority    | —           |

## Goal

Update `complete-task.sh` so that when a subtask is marked complete with
`--parent`, it renames the subtask directory to add an `X-` prefix:

```
c98d7b-0001-update-templates/  →  X-c98d7b-0001-update-templates/
```

The subtask list entry in the parent README is already updated to `[x]`
by the existing script logic; this adds the matching filesystem rename so
the tree is readable without opening any files.

All other references to the subtask path (e.g. in the parent README link)
must be updated to reflect the new `X-` prefixed name.

## Context

The `X-` prefix makes task progress immediately visible when browsing the
filesystem or reading `list-tasks.sh` output — no need to open READMEs to
check status.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
