# Task: audit-agent-prompts-for-stale-instructions

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

Audit all agent role prompts (`roles/*.md`) for instructions that describe
the old README-based task document model and update them to reflect the
current `task.json`-authoritative model. Remove or correct any instruction
that tells agents to read from or write to the job document (README) for
fields that are now injected inline by the orchestrator.

## Context

The pipeline communication architecture has changed significantly across this
task (49352f). Agents no longer need to read the job README for design fields,
context, or test commands — the orchestrator injects these inline into the
prompt via `task.json`. However, the role prompts have not been fully updated
to reflect this.

**Known stale instructions to check:**

| File | Stale instruction | Current reality |
|------|-------------------|-----------------|
| `ARCHITECT.md` | "The job document is a task README. Edit it in place — fill in the named sections" | Agents do not edit the task README; output goes to `task.json` fields or the output directory |
| `ARCHITECT.md` | "Fill in the `## Suggested Tools` section of the job document" | `suggested_tools` is a field in `task.json`, injected inline by the orchestrator |
| `ARCHITECT.md` | Trigger conditions check `Complexity:` in the job document | `complexity` is read from `task.json` by the orchestrator, not by the agent reading the README |
| `TASK_MANAGER.md` | "path to the task README" as the primary handoff to ARCHITECT | The orchestrator injects `task.json` fields inline; the README path is secondary |
| `DOCUMENTER.md` | References to the job document path | DOCUMENTER operates on the output directory, not the job document |

**What to do for each prompt:**
1. Identify every instruction that refers to reading from or writing to the
   job README as a communication mechanism
2. Determine whether the field/section is now injected inline (→ remove the
   instruction to read it), written to `task.json` (→ update to reflect that),
   or still legitimately in the README (→ keep)
3. Update the instruction to match current behaviour
4. Ensure each prompt accurately describes what the agent receives as input
   and what it is expected to produce as output

**Guiding principle:** agents should be told what they receive (inline prompt
content from the orchestrator) and what they produce (JSON response block,
files written to output dir). Instructions to "fill in sections of the job
document" are a relic of the old model and should be removed or replaced.

## Deliverable: Agent Role Summary Document

As part of this task, produce a concise reference document
(`ai-builder/orchestrator/agent-roles.md`) that summarises every agent in the
pipeline — both AI and internal — in one place. This document is the canonical
answer to "what does each agent do?".

**Cover every agent in `machines/default.json`:**

| Agent | Type | Receives | Produces | Valid outcomes |
|-------|------|----------|----------|----------------|
| ARCHITECT | AI (claude/gemini) | Inline: goal, context, complexity, handoff history | JSON block: outcome, handoff, design/components | `ARCHITECT_DESIGN_READY`, `ARCHITECT_DECOMPOSITION_READY`, `ARCHITECT_NEEDS_REVISION`, `ARCHITECT_NEED_HELP` |
| IMPLEMENTOR | AI (claude/gemini) | Inline: goal, design, acceptance criteria, handoff history | Files written to output dir; JSON block: outcome, handoff | `IMPLEMENTOR_IMPLEMENTATION_DONE`, `IMPLEMENTOR_NEEDS_ARCHITECT`, `IMPLEMENTOR_NEED_HELP` |
| DECOMPOSE_HANDLER | Internal | Components array from ARCHITECT JSON; job doc path | Pipeline subtask directories created; `current-job.txt` advanced | `HANDLER_SUBTASKS_READY`, `HANDLER_STOP_AFTER`, `HANDLER_NEED_HELP` |
| LEAF_COMPLETE_HANDLER | Internal | `current-job.txt`; output dir | `complete-task.sh` run; directory renamed to `X-`; `current-job.txt` advanced | `HANDLER_SUBTASKS_READY`, `HANDLER_ALL_DONE`, `HANDLER_STOP_AFTER`, `HANDLER_NEED_HELP` |
| TESTER | Internal | `test_command` from `task.json` | subprocess exit code | `TESTER_TESTS_PASS`, `TESTER_TESTS_FAIL`, `TESTER_NEED_HELP` |
| DOCUMENTER_POST_ARCHITECT | Internal | Job doc path; output dir | `.md` files indexed into output dir README | `DOCUMENTER_DONE` |
| DOCUMENTER_POST_IMPLEMENTOR | Internal | Job doc path; output dir | `.md` files indexed into output dir README | `DOCUMENTER_DONE` |

The table above is a starting point — the document should expand each entry
with a paragraph describing the agent's responsibility, its position in the
pipeline, and any non-obvious behaviour (e.g. DECOMPOSE_HANDLER's dual tree
writes, LCH's two-phase frame pop, TESTER's reliance on `task.json` rather
than direct injection).

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
