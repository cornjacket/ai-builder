# Task: per-role-model-tiering

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | —               |
| Priority    | HIGH        |
| Category    | gemini-compat          |
| Next-subtask-id | 0000               |

## Goal

Assign the most cost-appropriate model to each role: cheapest capable
model for simple roles (TESTER), most capable model for high-judgement
roles (ARCHITECT). Implement via the `"model"` field in machine JSON
(see `4f9fba-add-model-selection-to-machine-config`).

## Context

All AI roles currently use the same model (the CLI default). Cost and
quality are not uniformly distributed:

- **TESTER** — runs a single shell command, reads pass/fail output. No
  complex reasoning required. Good candidate for `claude-haiku-4-5` (5×
  cheaper than Sonnet, 25× cheaper than Opus).
- **IMPLEMENTOR** — writes code. Needs solid reasoning but not the highest
  capability. Sonnet is the right default.
- **ARCHITECT** — makes structural design decisions that cascade into all
  downstream work. Errors here are expensive to recover from. Good
  candidate for `claude-opus-4-6`.

**Open design question — split ARCHITECT role:**
The current ARCHITECT role serves two modes: System Architect (top-level
decomposition of a composite task) and Component Architect (design mode
for a single atomic task). These are very different in terms of required
capability and impact:
- System Architect decomposition decisions shape the entire component tree.
  This warrants Opus.
- Component Architect for a leaf task is simpler, perhaps Sonnet-appropriate.

Consider whether a separate `SYSTEM_ARCHITECT` role (used for Decompose
mode) and `COMPONENT_ARCHITECT` role (used for Design mode) would allow
tighter model selection and cleaner prompt separation.

**Prerequisite:** `4f9fba-add-model-selection-to-machine-config` must be
implemented before this task can be tested end-to-end.

**Reference:** `learning/agent-model-selection.md`

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
