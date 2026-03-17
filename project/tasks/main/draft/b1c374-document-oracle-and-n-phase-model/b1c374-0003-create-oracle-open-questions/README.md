# Subtask: create-oracle-open-questions

| Field    | Value                |
|----------|----------------------|
| Status   | —                    |
| Epic     | main             |
| Tags     | —             |
| Parent   | b1c374-document-oracle-and-n-phase-model           |
| Priority | —         |

## Description

Create `ai-builder/oracle/open-questions.md` with unresolved Oracle-layer
questions from the brainstorm.

Questions to capture:
1. Oracle role definition — does it need `roles/ORACLE.md` or is it fully
   defined by the target repo's `CLAUDE.md`?
2. Planning tools — what tools should ARCHITECT have in Planning mode that
   are not available in Implementation? How are they scoped?
3. Pipeline mode signalling — how does the TM know whether it's in Planning
   or Implementation mode? (job template type, `## Mode:` field, or `--mode` flag)
6. `project/reviews/` structure — freeform markdown or structured format?
   What fields? Git-tracked?
7. Oracle continuity — state reconstruction design; confirm no state exists
   only in conversation context
8. Error escalation — if TESTER fails and IMPLEMENTOR cannot fix, Oracle
   surfaces to human regardless of Stop-after
9. Parallel subtask implementation — could Oracle submit multiple pipeline
   runs in parallel for independent subtasks? (deferred optimisation)

Note: questions #4 and #5 belong in the decomposition task
(`7e7184-design-decomposition-protocol`), not here.

## Notes

_None._
