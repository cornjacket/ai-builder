# Subtask: run-pipeline-and-verify

| Field       | Value                                                                        |
|-------------|------------------------------------------------------------------------------|
| Status      | complete                                                                     |
| Epic        | main                                                                         |
| Tags        | —                                                                            |
| Parent      | 8eea17-implement-decomposition-in-orchestrator/d5dad2-add-decomposition-regression-test |
| Priority    | —                                                                            |
| Complexity  | —                                                                            |
| Stop-after  | true                                                                         |

## Description

Run the full decomposition pipeline against the user-service test and verify
the gold test suite passes. This is the final integration check.

**Steps:**
1. Run `tests/regression/user-service/reset.sh` to prepare the target repo
2. Run the orchestrator in TM mode:
   ```
   python ai-builder/orchestrator/orchestrator.py \
       --target-repo /tmp/ai-builder-test-user-service \
       --output-dir /tmp/ai-builder-test-user-service-output \
       --epic main
   ```
3. Monitor the execution log for correct routing:
   - ARCHITECT → `COMPONENTS_READY` → TASK_MANAGER
   - TASK_MANAGER → `JOBS_READY` → ARCHITECT (×N components)
   - Each component: ARCHITECT → `COMPONENT_READY` → IMPLEMENTOR → `IMPLEMENTATION_DONE` → TESTER → `TESTS_PASS` → TASK_MANAGER
   - Final: TASK_MANAGER → `ALL_DONE`
4. Run the gold test suite against the assembled output
5. All gold tests must pass

**Stop-after is `true`** — Oracle must review the pipeline output before the
regression test is considered stable.

## Notes

This subtask depends on all three preceding subtasks being complete:
`ceca3e-create-test-scaffold`, `b7f3a1-write-job-document-template`,
`e2d4c8-write-gold-test-suite`.
