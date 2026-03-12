# Task: review-orchestrator-routing-and-flow

| Field    | Value                |
|----------|----------------------|
| Status   | backlog           |
| Epic     | main             |
| Tags     | orchestrator, review             |
| Parent   | —           |
| Priority | HIGH         |

## Description

Formally review the orchestrator routing logic and flow documentation to
ensure they are correct, complete, and consistent with each other.

Review scope:
- `ai-builder/orchestrator.py` — ROUTES table, TM mode vs non-TM mode
  branching, state file handling, prompt construction for all roles
- `ai-builder/FLOW.md` — TM mode diagram, non-TM mode diagram, routing
  tables, data flow; verify they accurately reflect the code

Specific questions to answer:
- Are all valid OUTCOME values for each role represented in ROUTES?
- Does the TM loop-back correctly handle edge cases (empty backlog, task
  already complete)?
- Is the `current-task.txt` state file approach robust enough, or does it
  need a richer format (e.g. JSON with task name + epic)?
- Does FLOW.md accurately describe both modes after the TASK_MANAGER
  addition?

Deliverable: a written review with any issues found and fixes applied.

## Documentation

Update `ai-builder/FLOW.md` and `ai-builder/orchestrator.py` if issues
are found during review.

## Subtasks

<!-- When a subtask is finished, run complete-subtask.sh to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

**Role prompt injection question (to resolve during review):**
The TM prompt has dynamic content injected at runtime (target repo path,
script paths, epic, request text). The ARCHITECT, IMPLEMENTOR, and TESTER
prompts are currently static strings. As role definitions are extracted to
`roles/*.md` files and potentially expanded, we need to decide:

- Should role files be loaded verbatim (static text only), with dynamic
  content appended by the orchestrator at runtime?
- Or should role files support placeholders (e.g. `{{TARGET_REPO}}`) that
  the orchestrator substitutes before sending to the agent?
- If placeholders, what is the substitution mechanism and who owns the
  list of valid placeholders?

The current TM prompt mixes static role definition with dynamic runtime
context in a single f-string. This is hard to maintain as prompts grow.
A clean separation would be: role file = static identity and rules;
orchestrator injects = runtime context (paths, job doc, output dir).
