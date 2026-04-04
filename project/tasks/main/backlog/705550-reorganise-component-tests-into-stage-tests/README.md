# Task: reorganise-component-tests-into-stage-tests

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | testing, pipeline, orchestrator               |
| Priority    | MED           |
| Category    | regression-infra       |
| Next-subtask-id | 0000               |

## Goal

Move `tests/regression/user-service/component-tests/` to a new top-level
`tests/stage/` directory and restructure as self-contained, per-role stage
tests — one directory per agent/role under test, named
`<role>-<pipeline>` (e.g. `architect-user-service`, `implementor-user-service`).
Each test must own its own sandbox state (no shared paths with other tests).

## Context

The current component tests live inside `tests/regression/user-service/` and
share sandbox paths (`sandbox/user-service-target/`, `sandbox/user-service-output/`)
with the full regression runs and with each other. This creates two problems:

1. **Shared sandbox prevents concurrent runs.** Two stage tests cannot run at
   the same time, and running a stage test while a regression is in progress
   would corrupt both.

2. **Placement is wrong.** Stage tests are not regression tests — they test one
   pipeline stage from a known checkpoint, not the full pipeline end-to-end.
   They belong in their own top-level category alongside `unit/` and `regression/`.

The new structure:

```
tests/
    unit/                           — fast, no agents, no filesystem side effects
    stage/                          — single-step pipeline stage tests
        architect-user-service/     — ARCHITECT decompose: TOP task → component list
        decompose-handler-user-service/ — DECOMPOSE_HANDLER: components → subtask tree
        implementor-user-service/   — IMPLEMENTOR: design → source files
        tester-user-service/        — TESTER: test_command → pass/fail
        leaf-complete-handler-user-service/ — LCH: advance or complete pipeline
    regression/                     — full end-to-end pipeline runs
        fibonacci/
        user-service/
        platform-monolith/
```

Each stage test directory contains:
- `gold/` — committed snapshot of the sandbox state at the start of this stage
  (task tree + output dir; absolute paths rewritten to be repo-relative)
- `run.sh` — restores gold state to its own local sandbox, runs orchestrator,
  verifies expected outcome
- `README.md` — what is under test, how to run, how to re-capture gold state

**Self-contained sandbox:** each stage test uses its own sandbox subdirectory
(e.g. `sandbox/stage/architect-user-service/target/` and `.../output/`)
rather than the shared `sandbox/user-service-*` paths. No two stage tests
share sandbox space.

**No run archiving needed:** stage tests are fast, deterministic (modulo AI
non-determinism), and intended for rapid iteration. A pass/fail result is
sufficient; archiving runs to `runs/` is not required.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

**Absolute paths in gold state:** `task.json` files in the gold snapshots
contain absolute paths (e.g. `output_dir: /Users/david/.../sandbox/...`).
These will break on any machine other than the one that captured them, and
will break when the sandbox paths change under the new layout. The redesign
must address this — two options:

1. **Rewrite at restore time:** `run.sh` replaces the old absolute prefix
   with the current repo root when copying gold state into the sandbox.
2. **Store repo-relative in gold:** capture a relative path token
   (e.g. `__REPO_ROOT__/sandbox/stage/architect-user-service/output`) and
   expand it in `run.sh`.

Option 2 is cleaner — gold state is portable across machines. This is
probably the trickiest part of the implementation.
