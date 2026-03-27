# Task: architect-source-dir-in-decompose-json

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 49352f-redesign-pipeline-communication-architecture             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Add a `source_dir` field to each component in ARCHITECT's decompose-mode JSON
response. DECOMPOSE_HANDLER uses this path to create the correct output
subdirectory instead of deriving it from the component name.

## Context

**The bug:** DECOMPOSE_HANDLER creates `output_dir/component-name/` (e.g.
`iam/auth-lifecycle/`). ARCHITECT designs the actual package path (e.g.
`internal/iam/lifecycle/`). These diverge. README.md ends up in the pipeline
component dir; source ends up in the real package dir. IMPLEMENTOR, seeing the
mismatch, writes to both locations — producing identical duplicate files.

Observed in platform-monolith regression:
- `iam/auth-lifecycle/handler.go` (pipeline output dir copy)
- `internal/iam/lifecycle/handler.go` (actual package copy)
— both identical.

**Fix:** ARCHITECT decompose mode returns `source_dir` per component:

```json
{
  "outcome": "ARCHITECT_DECOMPOSITION_READY",
  "components": [
    {
      "name": "auth-lifecycle",
      "complexity": "atomic",
      "source_dir": "internal/iam/lifecycle",
      "description": "..."
    }
  ]
}
```

DECOMPOSE_HANDLER creates `output_dir/source_dir/` instead of
`output_dir/component-name/`. README.md, source code, and tests all land in
the same directory. IMPLEMENTOR receives the correct output_dir and writes
once.

**ARCHITECT.md** must be updated to require `source_dir` in the components
array for decompose mode. `source_dir` is the relative path within the output
directory where this component's source files will live.

**integrate component:** `source_dir` should be `.` or omitted — integrate
writes to the parent output dir directly (existing behaviour unchanged).

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
