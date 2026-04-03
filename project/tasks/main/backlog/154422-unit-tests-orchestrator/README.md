# Task: unit-tests-orchestrator

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status | backlog |
| Epic        | main               |
| Tags        | —               |
| Priority    | HIGH           |
| Created     | 2026-04-02            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

Make `orchestrator.py` (1,177 lines) unit-testable and write a meaningful test
suite covering its core logic: state machine loading, agent invocation routing,
metrics recording, and resume/clean-resume behaviour.

## Context

`orchestrator.py` is the most important untested file in the codebase. It is
currently untestable in unit form because it is a single large module where
pure logic (state machine traversal, outcome routing, prompt building) is
tightly coupled to subprocess calls, filesystem writes, and global mutable
state. Any test that touches `run_pipeline()` today would spawn real Claude/
Gemini subprocesses.

**Why this is a separate task from `f00df6`:**
Meaningful test coverage requires extracting pure functions from the monolith
first — this is a refactor task, not just a "write tests" task. The risk of
breaking the orchestrator during extraction warrants its own planning and review.

**Approach (to be refined in brainstorm/design subtask):**
1. Audit `orchestrator.py` for pure logic that can be extracted without
   behavioural change (state machine loading, outcome routing, prompt
   assembly, metrics aggregation).
2. Extract those functions/classes into testable units — likely a new
   `orchestrator_core.py` or similar module.
3. Mock the subprocess boundary (`agent_wrapper.py`) so orchestrator logic
   can be driven by fake agent responses.
4. Write tests against the extracted units. Target: 80%+ coverage of the
   extracted logic.

**Key logic to cover:**
- `load_state_machine()` — JSON parsing, `no_history` set construction, role resolution
- Outcome → next-state routing
- `build_prompt()` — history scoping, frame_stack, handoff assembly
- Entry-point validation (already tested separately in `test_orchestrator_validation.py`)
- Resume / clean-resume state recovery

## Notes

- Prerequisite: `f00df6` (run-unit-tests.sh + pytest infra) should be complete
  so new tests slot into the existing runner.
- Do NOT refactor for testability beyond what is needed — preserve all
  observable behaviour (same CLI, same state machine format, same output files).
- `agent_wrapper.py` subprocess boundary should be mockable via dependency
  injection or a thin wrapper interface; avoid monkey-patching.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
