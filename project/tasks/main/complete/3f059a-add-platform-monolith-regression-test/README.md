# Task: add-platform-monolith-regression-test

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status | complete |
| Epic        | main               |
| Tags        | regression-test, orchestrator |
| Priority    | HIGH                          |

## Goal

Run the platform-monolith regression test end-to-end and verify the pipeline
correctly handles a 3-level decomposition tree: platform → two services →
one service with two internal components.

## Context

The scaffolding for this test is committed at
`tests/regression/platform-monolith/`. It covers:
- Multi-level decomposition (3 levels deep for the IAM service)
- Level field propagation (TOP at build-1, INTERNAL at all internal integrates)
- Tree traversal via `on-task-complete.sh` walking up through composite nodes
- Two independent Go services (metrics on 8081, IAM on 8082)
- Gold tests in `gold/gold_test.go` verify both services end-to-end

This is the first regression test that exercises the full tree traversal
implemented in `0838a5-tm-tree-traversal`. Running it successfully would
validate the new advance-pipeline.sh / on-task-complete.sh scripts in a
realistic multi-level scenario.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
