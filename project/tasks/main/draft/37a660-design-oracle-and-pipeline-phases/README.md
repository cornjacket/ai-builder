# Task: design-oracle-and-pipeline-phases

| Field    | Value                |
|----------|----------------------|
| Status   | draft           |
| Epic     | main             |
| Tags     | oracle, orchestrator, design             |
| Parent   | —           |
| Priority | HIGH         |
| Next-subtask-id | 0009               |
## Description

Design and implement the Oracle (front-end AI) and the N-phase pipeline
architecture for ai-builder.

The Oracle is the human-facing AI process that conducts discovery, coordinates
pipeline phase transitions, manages the human review loop, and submits jobs to
the back-end orchestrator. It is the continuity layer across all pipeline
phases.

The N-phase model replaces the fixed 2-phase design with a flexible graph of
phases (Discovery, Planning, Implementation, Documentation, Review, Re-planning) connected
through the task system and `project/reviews/`.

**Reference:** `sandbox/brainstorm-oracle-and-n-phase-pipeline.md`

## Documentation

Document the Oracle role in `roles/ORACLE.md`. Update `ai-builder/FLOW.md`
with the N-phase model. Update `target/SETUP.md` and `project/tasks/README.md`
as needed.

## Subtasks

<!-- When a subtask is finished, run complete-subtask.sh to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [ ] [37a660-0000-define-oracle-role](37a660-0000-define-oracle-role/)
- [ ] [37a660-0001-design-reviews-directory](37a660-0001-design-reviews-directory/)
- [ ] [37a660-0002-add-reviews-directory-to-target](37a660-0002-add-reviews-directory-to-target/)
- [x] [X-37a660-0003-add-stop-after-to-subtask-template](X-37a660-0003-add-stop-after-to-subtask-template/)
- [ ] [37a660-0004-design-planning-mode-outcomes](37a660-0004-design-planning-mode-outcomes/)
- [ ] [37a660-0005-design-planning-tools-for-architect](37a660-0005-design-planning-tools-for-architect/)
- [ ] [37a660-0006-design-pipeline-mode-signalling](37a660-0006-design-pipeline-mode-signalling/)
- [ ] [37a660-0007-design-pipeline-regression-test](37a660-0007-design-pipeline-regression-test/)
- [ ] [37a660-0008-design-subagent-cwd-convention](37a660-0008-design-subagent-cwd-convention/)
<!-- subtask-list-end -->

## Notes

_None._
