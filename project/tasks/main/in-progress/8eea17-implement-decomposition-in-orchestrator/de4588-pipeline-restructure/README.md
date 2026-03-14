# Subtask: pipeline-restructure

| Field       | Value                                            |
|-------------|--------------------------------------------------|
| Status      | —                                                |
| Epic        | main                                             |
| Tags        | orchestrator, pipeline, restructure              |
| Parent      | 8eea17-implement-decomposition-in-orchestrator   |
| Priority    | —                                                |
| Complexity  | composite                                        |
| Stop-after  | false                                            |

## Description

Restructure the pipeline so that task READMEs are the job documents,
outcomes are prefixed with their source role, and TM drives service-level
testing after all subtasks complete.

Key changes:
- Task README = job document at every level (no separate JOB.md files)
- All pipeline outcomes renamed to `<ROLE>_<OUTCOME>` format
- Unified task template with all pipeline sections
- New PM scripts: `set-current-job.sh`, `subtasks-complete.sh`
- TM prompt updated for in-progress-only workflow and README-based job docs
- ARCHITECT prompt updated to fill named sections within task README
- `TM_LAST_SUBTASK_TESTS_PASS` route for service-level testing

## Subtasks

<!-- When a subtask is finished, run complete-subtask.sh to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [x] a1b2c3-rename-outcomes-with-role-prefix
- [x] b2c3d4-merge-task-templates-into-unified-template
- [x] c3d4e5-add-set-current-job-script
- [x] d4e5f6-add-subtasks-complete-script
- [x] e5f6a7-update-tm-prompt
- [x] f6a7b8-update-architect-prompt
- [x] a7b8c9-retire-standalone-job-templates
- [x] b8c9d0-add-tm-last-subtask-tests-pass-route
- [x] c9d0e1-update-regression-test-reset
<!-- subtask-list-end -->

## Notes

Must be completed before d5dad2-add-decomposition-regression-test is
considered stable — the regression test reset.sh and gold test were
written against the old JOB.md structure.
