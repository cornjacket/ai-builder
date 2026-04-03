# Task: bug-pipeline-no-readme-in-cmd-dirs

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Created     | 2026-04-03            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

Fix the pipeline so that it generates a `README.md` for every architecturally
relevant directory it creates, including `cmd/` and `cmd/<binary>/`.

## Context

Discovered during `8985d4-0007-verify-platform-monolith` gold test run.
`goldutil.CheckReadmeCoverage` reported:

```
missing README.md in architecturally relevant directory: cmd/
missing README.md in architecturally relevant directory: cmd/platform/
```

The IMPLEMENTOR writes the binary entry point at `cmd/platform/main.go` but
does not create a companion `README.md` in `cmd/` or `cmd/platform/`. The
documentation convention requires every directory to have a README.

**The `TestReadmeCoverage` check was removed from
`tests/regression/platform-monolith/gold/gold_test.go`** as a temporary
workaround so the gold tests can pass until this bug is fixed. When this
task is resolved, re-add `goldutil.CheckReadmeCoverage(t, outputDir)` to the
gold test.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
