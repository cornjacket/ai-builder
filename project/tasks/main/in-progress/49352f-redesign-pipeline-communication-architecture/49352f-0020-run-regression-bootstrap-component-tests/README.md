# Task: run-regression-bootstrap-component-tests

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

Run the user-service end-to-end regression test to validate all pipeline
changes from subtasks 0005–0011, then bootstrap the component test gold states
using `capture.sh` at each checkpoint.

## Context

Subtasks 0005–0011 made significant changes to the pipeline without an
intervening regression run: new ARCHITECT.md JSON output format, task.json as
single source of truth for IMPLEMENTOR/TESTER, frame stack serialization,
LCH two-phase pop, handoff state persistence, and the component test framework
itself. The component tests cannot be verified until the full pipeline runs
successfully and gold states are captured.

**Prerequisites:** subtask 0011 (pipeline-component-tests) complete.

**To complete this subtask:**
1. Run `tests/regression/user-service/reset.sh`
2. Run the orchestrator against user-service
3. Verify the pipeline completes + gold tests pass
4. Bootstrap gold states per `tests/regression/user-service/component-tests/README.md`
5. Run each component test step with `run.sh --expected-outcome`

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
