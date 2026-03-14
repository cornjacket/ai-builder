# Subtask: rename-outcomes-with-role-prefix

| Field       | Value                                                                 |
|-------------|-----------------------------------------------------------------------|
| Status      | —                                                                     |
| Epic        | main                                                                  |
| Tags        | —                                                                     |
| Parent      | 8eea17-implement-decomposition-in-orchestrator/de4588-pipeline-restructure |
| Complexity  | —                                                                     |
| Stop-after  | false                                                                 |

## Description

Rename all pipeline outcome constants to include the source role as a
prefix, and apply two name corrections:

| Old | New |
|-----|-----|
| `DONE` | `ARCHITECT_DESIGN_READY` |
| `COMPONENT_READY` | `ARCHITECT_DESIGN_READY` (merged with DONE) |
| `COMPONENTS_READY` | `ARCHITECT_DECOMPOSITION_READY` |
| `NEEDS_REVISION` | `ARCHITECT_NEEDS_REVISION` |
| `NEED_HELP` (ARCHITECT) | `ARCHITECT_NEED_HELP` |
| `IMPLEMENTATION_DONE` | `IMPLEMENTOR_IMPLEMENTATION_DONE` |
| `NEEDS_ARCHITECT` | `IMPLEMENTOR_NEEDS_ARCHITECT` |
| `NEED_HELP` (IMPLEMENTOR) | `IMPLEMENTOR_NEED_HELP` |
| `TESTS_PASS` | `TESTER_TESTS_PASS` |
| `TESTS_FAIL` | `TESTER_TESTS_FAIL` |
| `NEED_HELP` (TESTER) | `TESTER_NEED_HELP` |
| `JOBS_READY` | `TM_SUBTASKS_READY` |
| `ALL_DONE` | `TM_ALL_DONE` |
| `STOP_AFTER` | `TM_STOP_AFTER` |
| `NEED_HELP` (TM) | `TM_NEED_HELP` |

Update everywhere outcomes appear: ROUTES dict, valid_outcomes in
build_prompt(), all role prompt files (ARCHITECT.md, IMPLEMENTOR.md,
TESTER.md), TM prompt in orchestrator.py, and routing.md.
