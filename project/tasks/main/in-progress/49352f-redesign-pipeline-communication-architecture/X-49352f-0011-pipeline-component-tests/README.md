# Task: pipeline-component-tests

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

Build a chain of single-step gold-state regression tests for the user-service
pipeline. Each test exercises one agent plus its downstream internal handlers,
using a saved snapshot of task tree + output directory + `handoff-state.json`
as the gold input.

## Context

Full end-to-end regression runs are slow and require a live target repo. As
agents change during the pipeline redesign, we need a faster, targeted way to
verify each agent independently. The component test chain enables this.

**Structure of each component test:**

1. **Gold input** — three parts saved alongside the test:
   - Task tree snapshot: `project/tasks/` directory at the start point
   - Output directory snapshot: the `output/` directory at the start point
   - `handoff-state.json`: the serialized `handoff_history` + `frame_stack`
     at the start point (produced by subtask 0014)

2. **Run** — copy the gold input into the sandbox, start the orchestrator with
   `--start-state <AGENT_STATE>`, stop after that agent and its handlers via
   `stop-after` in `task.json`, inject handoff history via `--handoff-file`.

3. **Verify** — check that the orchestrator reached the expected stop state and
   that output files match expectations.

**Gold inputs are chained:** the gold output of step N becomes the gold input
for step N+1. This means a single full regression run can generate the entire
chain of gold states, which then serves as the baseline for all future
single-step tests.

**Key constraint:** the component test must exercise the orchestrator's
prompt-building code — the code that combines `task.json`, handoff history, and
the role prompt into the final agent input. Pre-building and injecting a golden
prompt directly would bypass this path and miss regressions in prompt assembly.

**Requires subtask 0014** (handoff-state persist-and-inject) to be complete
before this subtask can be implemented.

**Scope:** initial chain covers the user-service pipeline (ARCHITECT-decompose,
ARCHITECT-store, IMPLEMENTOR-store, TESTER-store, ARCHITECT-handlers,
IMPLEMENTOR-handlers, TESTER-handlers, ARCHITECT-integrate, IMPLEMENTOR-integrate,
TESTER-integrate).

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
