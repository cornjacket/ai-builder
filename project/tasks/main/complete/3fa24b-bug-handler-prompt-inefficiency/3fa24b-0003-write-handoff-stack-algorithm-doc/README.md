# Task: write-handoff-stack-algorithm-doc

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status      | —                      |
| Epic        | main               |
| Tags        | —               |
| Parent      | 3fa24b-bug-handler-prompt-inefficiency             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Produce a checked-in design document describing the handoff stack algorithm so that
implementors have a precise specification to work from and the design decision is
recorded permanently.

## Context

The algorithm is drafted in `b14e76-brainstorm-token-usage-and-caching-costs` (the
"Proposed Algorithm" section, dated 2026-03-18). That brainstorm is the source of truth
during design. This subtask is to extract and formalise it into a permanent doc.

Output: `ai-builder/orchestrator/handoff-stack.md`

The document should cover:
- Problem statement (append-only list, context leaks across siblings)
- Data structures: `handoff_history`, `frame_stack`, `Frame` fields
- Push rule (on DECOMPOSE_HANDLER)
- Pop rule (on LEAF_COMPLETE_HANDLER, both cases: sibling and level-change)
- Illustrated trace using the platform-monolith tree
- Table showing what each role sees at each point
- Why `scope_dir = job_doc.parent` is the correct comparator
- Open question: should the LEAF handoff entry be kept before truncation?
- Implementation notes (truncation syntax, no changes to `build_prompt`)

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
