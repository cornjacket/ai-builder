# Task: implement-pm-role

| Field    | Value                                         |
|----------|-----------------------------------------------|
| Status | complete |
| Epic     | main                                          |
| Tags     | project-management, orchestrator              |
| Parent   | 651a51-add-project-management-system-template |
| Priority | HIGH                                          |

## Description

Wire the PROJECT MANAGER role into the orchestrator pipeline.

- Add PM as the first stage in the pipeline, before ARCHITECT
- PM receives the project request, initialises the task system in the target
  repo (via setup-project.sh / init-claude-md.sh if not already present),
  decomposes work into tasks, then hands the first task to the ARCHITECT
- After TESTER signs off on a task, control returns to the PM to mark it
  complete and select the next task
- Pipeline loop continues until PM determines all tasks are complete
- Depends on: `design-pm-role`, `write-setup-script`, `write-claude-md-init-script`
- Orchestrator lives at `ai-builder/orchestrator.py` (not sandbox)

## Documentation

Update `ai-builder/FLOW.md` after wiring the PROJECT_MANAGER into the
pipeline — both the flow diagram and the routing table.

## Subtasks

<!-- When a subtask is finished, run complete-subtask.sh to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

- Pipeline documents are called "jobs" (not tasks) to avoid collision with the
  project management task system. Templates and files use `JOB-` prefix:
  `ai-builder/JOB-TEMPLATE.md`, `current-job.txt`, `--job` CLI flag.
- PM creates a job document per task by populating `JOB-TEMPLATE.md` with the
  task README's Description as the Goal section. Job doc is written to
  `output_dir/<task-name>.md` (interim location — see
  `284735-design-orchestrator-output-directory` for long-term design).
- PM outcome signals renamed: `TASKS_READY` → `JOBS_READY`.
- `PM_SCRIPTS_DIR` (was `TASK_SCRIPTS_DIR`) points to the target repo's
  project management scripts (`project/tasks/scripts/`), not pipeline scripts.
