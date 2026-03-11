# Task: design-oracle-and-pipeline-phases

| Field    | Value                |
|----------|----------------------|
| Status   | draft           |
| Epic     | main             |
| Tags     | oracle, orchestrator, design             |
| Parent   | —           |
| Priority | HIGH         |

## Description

Design and implement the Oracle (front-end AI) and the N-phase pipeline
architecture for ai-builder.

The Oracle is the human-facing AI process that conducts discovery, coordinates
pipeline phase transitions, manages the human review loop, and submits jobs to
the back-end orchestrator. It is the continuity layer across all pipeline
phases.

The N-phase model replaces the fixed 2-phase design with a flexible graph of
phases (Discovery, Planning, Implementation, Review, Re-planning) connected
through the task system and `project/reviews/`.

**Reference:** `sandbox/brainstorm-oracle-and-n-phase-pipeline.md`

## Documentation

Document the Oracle role in `roles/ORACLE.md`. Update `ai-builder/FLOW.md`
with the N-phase model. Update `target/SETUP.md` and `project/tasks/README.md`
as needed.

## Subtasks

<!-- When a subtask is finished, run complete-subtask.sh to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [ ] [7226c5-define-oracle-role](7226c5-define-oracle-role/)
- [ ] [9b9d18-design-reviews-directory](9b9d18-design-reviews-directory/)
- [ ] [dcdf24-add-stop-after-to-subtask-template](dcdf24-add-stop-after-to-subtask-template/)
- [ ] [dd2d56-add-reviews-directory-to-target](dd2d56-add-reviews-directory-to-target/)
- [ ] [918f07-design-planning-mode-outcomes](918f07-design-planning-mode-outcomes/)
- [ ] [f58844-design-planning-tools-for-architect](f58844-design-planning-tools-for-architect/)
- [ ] [5e26c5-design-pipeline-mode-signalling](5e26c5-design-pipeline-mode-signalling/)
- [ ] [e975fc-design-pipeline-regression-test](e975fc-design-pipeline-regression-test/)
- [ ] [2c2130-design-subagent-cwd-convention](2c2130-design-subagent-cwd-convention/)
<!-- subtask-list-end -->

## Notes

_None._
