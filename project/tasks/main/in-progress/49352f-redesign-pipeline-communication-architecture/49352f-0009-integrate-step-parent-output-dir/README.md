# Task: integrate-step-parent-output-dir

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status      | —                      |
| Epic        | main               |
| Tags        | —               |
| Parent      | 49352f-redesign-pipeline-communication-architecture             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Configure DECOMPOSE_HANDLER to set `integrate`'s `output_dir` to the parent's
output directory rather than creating a new subdirectory. Update ARCHITECT's
integrate-mode prompt to make the "no new docs" rule explicit. Ensure the
orchestrator reads `output_dir` from `task.json` rather than constructing a
path from the component name.

## Context

`integrate` is a special component at every decomposition level. It wires
existing components together — it does not produce new source files in a new
package directory. Wiring code (e.g. `main.go`, dependency injection, package
init) belongs in the parent output directory alongside the component packages.
Creating an `integrate/` subdirectory would be wrong.

**DECOMPOSE_HANDLER behavior for `integrate`:**
- No output subdirectory created (all other components get one)
- `output_dir` in `task.json` set to the parent component's `output_dir`
  (e.g. `user-service-output/`, not `user-service-output/integrate/`)

**ARCHITECT atomic mode for `integrate`:**
- `documents_written: false` always — parent ARCHITECT already produced docs
  during decompose mode; `integrate` adds no new documentation
- DOCUMENTER does not run after `integrate`
- The prompt must make this explicit to prevent ARCHITECT from writing
  redundant docs

**`task.json` for `integrate`:**
```json
{
  "name": "integrate",
  "complexity": "atomic",
  "output_dir": "/path/to/parent/output/dir"
}
```

**Dependency:** subtask 0003 (DECOMPOSE_HANDLER dual tree) must be complete
before this subtask is implemented.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
