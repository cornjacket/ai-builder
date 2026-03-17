# Task: improve-regression-test-infrastructure

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | regression, testing |
| Priority    | MED                 |

## Goal

Improve the regression test infrastructure to reduce wasted compute from
framework bugs and make it easier to add new regression tests correctly.

## Context

A misassigned `targetDir` variable in the platform-monolith gold test
pointed at the task repo instead of the output dir. The failure was silent
at setup time and only surfaced after a full pipeline run completed.
Framework bugs should be catchable without running the pipeline.

Two improvements are needed:

**1. Shared gold test utilities (`goldutil` package)**

Every regression test reimplements the same helpers: `findMainPackages`,
`buildBinary`, `waitReady`, `extractField`, `TestMain` setup, and
directory path logic. This creates duplicate surfaces for bugs — a wrong
path assumption gets copied silently into each new test.

Extract a shared `tests/regression/goldutil/` Go package containing all
reusable framework mechanics. Each test's `gold_test.go` imports it and
focuses only on the API assertions specific to that test. Bugs in the
framework are fixed once; the package interface makes assumptions (e.g.
`OutputDir`) explicit and reviewable.

**2. Regression test infrastructure smoke test**

Add a `tests/regression/infra-smoke/` test that validates the gold test
framework itself without running the pipeline. It uses committed minimal
fixture code — a stub Go binary that starts HTTP listeners on configurable
ports and returns 200 — to confirm that:
- `findMainPackages` locates the correct binary
- `buildBinary` compiles successfully
- `waitReady` correctly detects a live listener
- `TestMain` setup/teardown completes without I/O timeout

This smoke test runs in seconds and should be the first check before any
full pipeline regression run. If the smoke test fails, a framework bug
exists and there is no point running the pipeline until it passes.

The fixture binary is intentionally minimal and committed to the repo —
it only needs to satisfy `waitReady`, so drift risk is low.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
