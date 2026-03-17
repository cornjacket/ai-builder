# Task: analyze-tm-prompt-for-ai-reduction

| Field       | Value                        |
|-------------|------------------------------|
| Task-type   | USER-SUBTASK                 |
| Status | complete |
| Epic        | main                         |
| Tags        | orchestrator, tm             |
| Parent      | 0838a5-tm-tree-traversal     |
| Priority    | —                            |

## Goal

Analyze the current TM prompt in `orchestrator.py` and produce a clear
inventory of: (a) operations that still require AI judgment, and (b) operations
that are deterministic and could be moved into scripts. Do not implement
any changes — this is a research and analysis task only. Output should be
a written analysis with specific recommendations for follow-on work.

## Context

The prompt is the least reliable part of the system — it is probabilistic by
nature. Every field read, boolean check, and procedural step left in the prompt
is a surface for non-deterministic failure. Scripts run the same way every time.

**Operations that likely belong in scripts, not the prompt:**
- Reading any field from a README (Level, Stop-after, Complexity, Task-type)
- Checking any boolean condition (is-top-level, check-stop-after)
- Any procedural sequencing that doesn't require judgment

**Operations that likely need AI:**
- Parsing the Components table and extracting structured data
- Deciding ordering of components by implementation dependency
- Writing the Goal and Context sections for each new subtask

**Constraint for any future implementation:** scripts are called by the TM
agent — do not integrate them into the orchestrator core. The orchestrator
must remain agnostic of the task management system.

## Subtasks

<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

Analysis complete. Findings written to follow-on task in backlog.
