# Subtask: update-tm-prompt

| Field       | Value                                                                 |
|-------------|-----------------------------------------------------------------------|
| Status | complete |
| Epic        | main                                                                  |
| Tags        | —                                                                     |
| Parent      | 8eea17-implement-decomposition-in-orchestrator/de4588-pipeline-restructure |
| Complexity  | —                                                                     |
| Stop-after  | false                                                                 |

## Description

Update the TASK_MANAGER prompt in orchestrator.py to reflect the
restructured pipeline:

- Replace the dispatch on is_first_run / last_outcome with a clean
  table: ARCHITECT_DECOMPOSITION_READY → create subtasks;
  TESTER_TESTS_PASS → mark done, check subtasks-complete.sh
- All subtask creation uses --folder in-progress --parent <parent>
  (never --folder draft, never without --parent)
- Use set-current-job.sh to update current-job.txt (not raw file writes)
- TM writes Goal and Context directly into the subtask README sections
  (not a separate JOB.md file in the output dir)
- Remove move-task.sh from TM's available tools — not needed in pipeline
- Add subtasks-complete.sh to TM's available tools
- Use updated outcome names (TM_SUBTASKS_READY, TM_ALL_DONE, etc.)

The Available Tools section should list only what TM needs in the
pipeline context:
  new-task.sh        --epic <epic> --folder in-progress --parent <parent> --name <name>
  complete-task.sh   --epic <epic> --folder in-progress --parent <parent> --name <id-name>
  subtasks-complete.sh --epic <epic> --folder in-progress --parent <parent>
  set-current-job.sh --output-dir <dir> <task-readme-path>
  list-tasks.sh      --epic <epic> --folder in-progress --depth 2
