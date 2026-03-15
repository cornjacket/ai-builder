# Task: add-project-management-scripts

| Field       | Value         |
|-------------|---------------|
| Task-type   | USER-SUBTASK  |
| Status | complete |
| Epic        | main          |
| Tags        | —             |
| Parent      | f7a6af-redefine-task-system-human-pipeline-boundary |
| Priority    | —             |

## Goal

Add scripts for creating epics, projects, and pipeline builds. Covers both
`project/tasks/` (via `new-epic.sh`) and `project/projects/` (via
`new-project.sh`, `new-build.sh`, `list-projects.sh`).

## Context

`new-epic.sh` — create an epic with all status subdirectories:
```bash
new-epic.sh --name main
# Creates project/tasks/main/ with inbox, draft, backlog, in-progress, complete, wont-do

new-epic.sh --name main --project my-project
# Creates project/projects/my-project/main/ with same structure
```

`new-project.sh` — create a new project and its default main epic:
```bash
new-project.sh --name my-project
# Creates project/projects/my-project/README.md (user-task-template)
# Then calls new-epic.sh --name main --project my-project internally
```
Result:
```
project/projects/
    my-project/
        README.md      ← user-task
        main/          ← epic
            inbox/
            draft/
            backlog/
            in-progress/
            complete/
            wont-do/
```

`new-build.sh` — create a pipeline-subtask (build-N) under a project:
```bash
new-build.sh --project my-project --name build-1
# Creates project/projects/my-project/build-1/README.md (pipeline-build-template)
```

`list-projects.sh` — list all projects with their builds and status:
```bash
list-projects.sh
# Shows each project and its build-N subdirectories with status
```

All scripts go in both `project/tasks/scripts/` and `target/project/tasks/scripts/`.

**Note:** Other task scripts will later gain a `--project` flag to operate on
`project/projects/{name}/{epic}/` instead of `project/tasks/{epic}/`. Deferred.

## Notes

`new-project.sh` and `new-build.sh` are wrappers around `new-user-task.sh`
and `new-pipeline-subtask.sh` respectively, scoped to `project/projects/`.
`new-epic.sh` is a general-purpose script usable for both `project/tasks/`
and `project/projects/`.
