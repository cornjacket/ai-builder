# Subtask: define-oracle-role

| Field    | Value                |
|----------|----------------------|
| Status   | —                    |
| Epic     | main             |
| Tags     | oracle, design             |
| Parent   | 37a660-design-oracle-and-pipeline-phases           |
| Priority | HIGH         |

## Description

Write the Oracle role definition and the ai-builder workflow document.

**Deliverables:**

1. `roles/ORACLE.md` — formal Oracle role definition covering:
   - Purpose and identity (the human-facing AI, the continuity layer)
   - Discovery conversation protocol and question template (purpose, tech
     stack, interfaces, constraints, scope, success criteria, review
     checkpoints)
   - How to read and reason about `project/tasks/`, `project/reviews/`,
     and `project/status/` to reconstruct project state
   - Phase coordination logic: how the Oracle decides what phase runs next
     based on task state, `Stop-after` flags, pipeline outcomes, and human
     input
   - How to build job documents and submit them to the pipeline
   - How to manage the human review loop

2. `ai-builder/WORKFLOW.md` — workflow document describing the full
   Oracle-driven N-phase pipeline for ai-builder users:
   - Discovery → Planning → Review → Implementation → Review → Re-planning
   - How each phase is triggered and what terminates it
   - The Oracle's role at each phase boundary
   - Example walkthrough of a complete feature from prompt to code

3. Update `target/init-claude-md.sh` to inject the Oracle instructions into
   the target repo's `CLAUDE.md` so the Oracle is available in any repo set
   up with the ai-builder template.

## Notes

Reference: `sandbox/brainstorm-oracle-and-n-phase-pipeline.md`
