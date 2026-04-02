# Task: add-master-index-gold-checks

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | b9529c-doc-pipeline             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Add a `TestMasterIndexExists` gold check to `doc-user-service` (and note the
same requirement for `doc-platform-monolith`). The orchestrator already
produces `master-index.md` at teardown via `build_master_index`; this subtask
just wires the check into the regression tests.

## Context

`master-index.md` is written to the root of `--output-dir` at the end of every
orchestrator run by `build_master_index(OUTPUT_DIR)` in `orchestrator.py`.
The doc pipeline produces it today — `sandbox/doc-user-service-output/master-index.md`
exists after a run — but `gold/gold_test.go` doesn't check for it.

**Change required:**

Add to `tests/regression/doc-user-service/gold/gold_test.go`:

```go
func TestMasterIndexExists(t *testing.T) {
    checkFile(t, "master-index.md")
}
```

The `doc-platform-monolith` gold test (subtask 0010, sub-subtask 0004) must
also include a `TestMasterIndexExists` check — that requirement is noted in
the 0010 subtask description.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
