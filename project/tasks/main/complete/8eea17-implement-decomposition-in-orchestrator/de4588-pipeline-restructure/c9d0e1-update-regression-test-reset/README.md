# Subtask: update-regression-test-reset

| Field       | Value                                                                 |
|-------------|-----------------------------------------------------------------------|
| Status | complete |
| Epic        | main                                                                  |
| Tags        | —                                                                     |
| Parent      | 8eea17-implement-decomposition-in-orchestrator/de4588-pipeline-restructure |
| Complexity  | —                                                                     |
| Stop-after  | true                                                                  |

## Description

Update tests/regression/user-service/reset.sh and re-run the full
pipeline to verify the restructured pipeline works end-to-end.

Changes to reset.sh:
- Populate the user-service task README with Goal, Context, Components
  sections (instead of creating a separate JOB-user-service.md)
- Use set-current-job.sh to point current-job.txt at the task README
- Remove JOB-user-service.md.template (no longer needed)
- Update work/.gitignore accordingly

After reset, run the pipeline and verify:
- ARCHITECT fills Components section of the task README
- TM creates subtasks in in-progress/, writes Goal/Context into each
  subtask README, uses set-current-job.sh
- Each component cycles through ARCHITECT/IMPLEMENTOR/TESTER correctly
- After last subtask: TM emits TM_LAST_SUBTASK_TESTS_PASS, TESTER runs
  service-level tests against parent task Acceptance Criteria
- Gold test suite passes

Stop-after: true — Oracle review required after first successful run
to verify the restructured output before declaring stable.
