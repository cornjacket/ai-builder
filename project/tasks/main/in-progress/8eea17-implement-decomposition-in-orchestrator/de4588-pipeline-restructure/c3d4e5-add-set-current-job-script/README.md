# Subtask: add-set-current-job-script

| Field       | Value                                                                 |
|-------------|-----------------------------------------------------------------------|
| Status      | —                                                                     |
| Epic        | main                                                                  |
| Tags        | —                                                                     |
| Parent      | 8eea17-implement-decomposition-in-orchestrator/de4588-pipeline-restructure |
| Complexity  | —                                                                     |
| Stop-after  | false                                                                 |

## Description

Add set-current-job.sh to the PM scripts. Writes the absolute path of a
task README to current-job.txt in the pipeline output directory.

Usage:
  set-current-job.sh --output-dir <pipeline-output-dir> <task-readme-path>

Used by:
- Oracle: before invoking the orchestrator, to seed the initial job
- TM: after selecting the next task, to update the active job pointer
- Reset scripts: during test setup

Add to both project/tasks/scripts/ and target/project/tasks/scripts/.
Document in project/tasks/README.md and target/project/tasks/README.md.
