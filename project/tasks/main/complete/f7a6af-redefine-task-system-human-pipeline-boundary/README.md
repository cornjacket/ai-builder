# Task: redefine-task-system-human-pipeline-boundary

| Field       | Value                                      |
|-------------|-------------------------------------------|
| Task-type   | USER-TASK                                  |
| Status | complete |
| Epic        | main                                       |
| Tags        | task-management, pipeline, documentation   |
| Priority    | HIGH                                       |

## Goal

Redefine the task system to cleanly separate human/frontend-AI tasks from
pipeline build subtasks. Introduce three distinct task types, each with its
own template and creation script. Update all documentation and restructure
existing in-flight tasks to match the new convention.

## Context

The current unified task template conflates concerns that belong to different
owners. There are three distinct task types:

**user-task** — top-level only. All top-level work must be a user-task.
Long-lived. Owned by the human/Oracle. Captures intent, context, decisions.
No Parent field. Uses `user-task-template.md`. Created with `new-user-task.sh`.

**user-subtask** — human/Oracle-owned subtask. Can live under a user-task
or another user-subtask. Used for planning steps, reviews, approvals,
research. Does not go to the pipeline. Has a Parent field. Uses
`user-subtask-template.md`. Created with `new-user-subtask.sh`.

**pipeline-subtask** — the pipeline's unit of work. Can live under a
user-task, user-subtask, or another pipeline-subtask. Authored by the
Oracle/human as `build-N`, then submitted to the orchestrator. Pipeline-owned
once submitted. Has a Parent field (can point to any type). Uses
`pipeline-build-template.md`. Created with `new-pipeline-subtask.sh`.

**Hierarchy rules:**
- All top-level work must be a user-task.
- user-task can contain user-subtasks and/or pipeline-subtasks.
- user-subtask can contain user-subtasks and/or pipeline-subtasks.
- pipeline-subtask can only contain pipeline-subtasks.
- No human-owned node may appear under a pipeline-owned node.

**Template identification:** Every template carries a `Task-type` field:
- `| Task-type | USER-TASK |`
- `| Task-type | USER-SUBTASK |`
- `| Task-type | PIPELINE-SUBTASK |`

**Script design:** Three precise scripts replace `new-task.sh`:
- `new-user-task.sh` — creates user-tasks using `user-task-template.md`
- `new-user-subtask.sh` — creates user-subtasks using `user-subtask-template.md`
- `new-pipeline-subtask.sh` — creates pipeline-subtasks using `pipeline-build-template.md`

`new-task.sh` is deprecated once all three are in place. The TM agent prompt
must be updated to call `new-pipeline-subtask.sh` instead of `new-task.sh --parent`.

Example structure:
```
project/tasks/main/in-progress/
    my-service/                    ← USER-TASK
        README.md
        review/                    ← USER-SUBTASK
            README.md
        build-1/                   ← PIPELINE-SUBTASK
            README.md
            auth-component/        ← PIPELINE-SUBTASK (internal)
                README.md
```

Full design context in:
- `sandbox/brainstorm-composite-decomposition-gap.md`
  (sections: "Task type identification", "Task type hierarchy rules",
  "Proposed redesign", "The filesystem is the implementation")

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [x] [d294c3-define-parent-task-template](d294c3-define-parent-task-template/)
- [x] [411984-define-user-subtask-template](411984-define-user-subtask-template/)
- [x] [32c156-define-pipeline-build-template](32c156-define-pipeline-build-template/)
- [x] [c8422d-update-project-tasks-readme](c8422d-update-project-tasks-readme/)
- [x] [191773-update-aibuilder-claude-md-two-task-domains](191773-update-aibuilder-claude-md-two-task-domains/)
- [x] [b148fe-update-target-claude-md-two-task-domains](b148fe-update-target-claude-md-two-task-domains/)
- [x] [933846-add-project-management-scripts](933846-add-project-management-scripts/)
<!-- subtask-list-end -->

## Notes

Restructuring applies only to tasks in `draft/`, `backlog/`, and `in-progress/`.
Tasks in `complete/` are historical record — do not touch them.

---

### Subtask descriptions

**d294c3-define-parent-task-template**

Produce `user-task-template.md` and `new-user-task.sh`. Template has no
Parent field and no pipeline sections. Includes `Task-type: USER-TASK`.
Documents all three task types and hierarchy rules.

**411984-define-user-subtask-template**

Produce `user-subtask-template.md` and `new-user-subtask.sh`. Template has
Parent field, no pipeline sections (no Complexity, Stop-after, Last-task,
Components, Design, AC, Suggested Tools). Includes `Task-type: USER-SUBTASK`.

**32c156-define-pipeline-build-template**

Produce `pipeline-build-template.md` and `new-pipeline-subtask.sh`. Template
has Parent field and all pipeline sections. Includes `Task-type: PIPELINE-SUBTASK`.
Deprecates `new-task.sh` once all three scripts exist.

**c8422d-update-project-tasks-readme**

Update `project/tasks/README.md` and `target/` copy to document all three
task types, hierarchy rules, new scripts, and the `project/projects/` convention.

**3f7ea4-restructure-existing-tasks**

Migrate all tasks in `draft/`, `backlog/`, `in-progress/` to the correct
template. Extract pipeline content into `build-1/` subtasks where needed.

**191773-update-aibuilder-claude-md-two-task-domains**

Update ai-builder's `CLAUDE.md` to document all three task types, hierarchy
rules, the two domains, and which script/template to use when.

**b148fe-update-target-claude-md-two-task-domains**

Update `target/init-claude-md.sh` and its CLAUDE.md template to inform both
the frontend AI and orchestrator/TM about all three task types and ownership.

**933846-add-project-management-scripts**

Add `new-project.sh`, `new-build.sh`, `list-projects.sh` for the
`project/projects/` convention. Wrappers around `new-user-task.sh` and
`new-pipeline-subtask.sh`.
