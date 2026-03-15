# Task: define-parent-task-template

| Field       | Value         |
|-------------|---------------|
| Status | complete |
| Epic        | main      |
| Tags        | —      |
| Parent      | f7a6af-redefine-task-system-human-pipeline-boundary    |
| Priority    | —  |

## Goal

Define `user-task-template.md` and `new-user-task.sh` — the template and
creation script for top-level human/Oracle-owned tasks. Documents all three
task types and when to use each.

## Context

There are three distinct task types in the redesigned system:

**user-task**: A top-level task created and owned by the human or Oracle.
Describes intent, context, and decisions. Long-lived. Contains user-subtasks
and/or pipeline-subtasks as children. Does not contain pipeline sections
(Components, Design, AC). Uses `user-task-template.md`.

**user-subtask**: A subtask under a user-task or user-subtask that is still
human/Oracle-owned. Used for planning steps, reviews, approvals, research,
or any work the human manages directly. Does not go to the pipeline. Can
contain further user-subtasks or pipeline-subtasks. Uses
`user-subtask-template.md`.

**pipeline-subtask**: A subtask (typically named `build-N`) that is the
pipeline's entry point. Authored by the Oracle/human, then submitted to the
orchestrator. Pipeline-owned once submitted. Can only contain pipeline-subtasks.
Uses `pipeline-build-template.md`.

Hierarchy rules:
- All top-level work must be a user-task.
- user-task can contain user-subtasks and/or pipeline-subtasks.
- user-subtask can contain user-subtasks and/or pipeline-subtasks.
- pipeline-subtask can only contain pipeline-subtasks.
- No human-owned node may appear under a pipeline-owned node.

This subtask produces `user-task-template.md` and documents the distinction
between all three types so it is clear which to use and when.

## Notes

**Template identification:** Each template must include a `Task-type` field
in its metadata table identifying its type:
- `user-task-template.md` → `| Task-type | USER-TASK |`
- `user-subtask-template.md` → `| Task-type | USER-SUBTASK |`
- `pipeline-build-template.md` → `| Task-type | PIPELINE-SUBTASK |`

**Script design:** Three separate scripts replace `new-task.sh`:
- `new-user-task.sh` — creates top-level user-tasks using `user-task-template.md`
- `new-user-subtask.sh` — creates user-subtasks using `user-subtask-template.md`
- `new-pipeline-subtask.sh` — creates pipeline-subtasks using `pipeline-build-template.md`

Each script is precise and unambiguous. No `--type` flag needed. `new-task.sh`
is deprecated once all three are in place.

**TM agent prompt side effect:** The TM currently calls `new-task.sh --parent`
to create pipeline component subtasks. It must be updated to call
`new-pipeline-subtask.sh` instead.
