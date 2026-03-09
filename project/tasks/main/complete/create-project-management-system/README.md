# Task: create-project-management-system

| Field  | Value                          |
|--------|--------------------------------|
| Status | complete  |
| Epic   | main                           |
| Tags   | project-management, tooling    |
| Parent | —                              |

## Description

Design and implement a directory-based task management system for the
ai-builder project. The system must be usable by both human developers and AI
coding agents. Tasks are represented as directories containing a `README.md`.
Status is conveyed by which status directory a task lives in. Subtasks are
subdirectories of their parent task.

The parent of a task is always its **containing directory**. For a top-level
task the parent is the status folder (`draft/`, `backlog/`, etc.). For a
subtask the parent is the task directory above it. The script always does the
same two things regardless of depth: create `<parent>/<name>/README.md` and
append to `<parent>/README.md`.

```
project/tasks/
    main/                        ← epic
        draft/                   ← status folder (parent of top-level tasks)
            README.md            ← updated when a top-level task is created
            some-task/           ← top-level task (parent = draft/)
                README.md
                some-subtask/    ← subtask (parent = some-task/)
                    README.md
```

The system includes:
- A documented directory structure under `project/tasks/<epic>/<status>/<task>/`
- Shell scripts for creating, moving, and listing tasks
- A task README template with a standardized metadata header
- `CLAUDE.md` and `GEMINI.md` at the repo root to orient AI agents

## Subtasks

<!-- When a subtask is finished, run complete-subtask.sh to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [x] [design-directory-structure](design-directory-structure/)
- [x] [write-scripts](write-scripts/)
- [x] [write-documentation](write-documentation/)
- [x] [add-agent-instruction-files](add-agent-instruction-files/)
- [x] [list-tasks-recursive-depth](list-tasks-recursive-depth/)
- [x] [list-tasks-root-option](list-tasks-root-option/)
- [x] [refine-task-management-scripts](refine-task-management-scripts/)
- [x] [nice-to-have-enhancements](nice-to-have-enhancements/)
- [x] [add-priority-field](add-priority-field/)
- [x] [add-short-id-to-task-names](add-short-id-to-task-names/)
- [x] [list-tasks-respect-readme-order](list-tasks-respect-readme-order/)
<!-- subtask-list-end -->

## Notes

- The first four subtasks are complete as of the initial implementation session.
  Two new subtasks added to improve list-tasks.sh.
- The CSV-based approach was considered and rejected in favour of the
  directory/README approach, which is more readable for AI agents and requires
  no separate tooling to stay in sync.
- `GEMINI.md` is a symlink to `CLAUDE.md` so both agents read the same file.
