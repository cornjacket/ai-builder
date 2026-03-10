# Subtask: design-reviews-directory

| Field    | Value                |
|----------|----------------------|
| Status   | —                    |
| Epic     | main             |
| Tags     | oracle, design             |
| Parent   | 37a660-design-oracle-and-pipeline-phases           |
| Priority | MED         |

## Description

Design the `project/reviews/` directory structure and review artifact format
for the target repo.

`project/reviews/` is a first-class project directory alongside `project/tasks/`
and `project/status/`. It stores code review artifacts written by the Oracle
after human review sessions. It is consulted by:
- The ARCHITECT during Planning (to avoid repeating past mistakes, factor in
  known debt, align with established patterns)
- The Oracle during Human Review (to accumulate and surface review history)
- The PM during Re-planning (to understand what went wrong)

**Questions to resolve:**

- What does a review artifact look like? Options:
  - Freeform markdown (flexible, easy to write, hard to query)
  - Structured format with defined fields (date, task, reviewer, findings,
    decision, follow-up actions)
  - Hybrid: structured header + freeform body
- How are review files named? By date, by task ID, by subtask?
- How does the ARCHITECT query `project/reviews/` during Planning? Does it
  read all files, or does the Oracle surface relevant ones in the job document?
- Should reviews be scoped to a specific task/subtask, or project-wide?
- Should `project/reviews/` be committed to git? (Likely yes — review history
  is valuable project memory)

**Deliverables:**
- A defined review artifact format (template file)
- Directory naming/organisation conventions
- Documentation of how reviews are created and consumed
- Add `project/reviews/` to `target/` skeleton (handled in a separate subtask)

## Notes

Reference: `sandbox/brainstorm-oracle-and-n-phase-pipeline.md`
