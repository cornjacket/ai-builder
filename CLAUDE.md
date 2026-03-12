# AI Agent Instructions — ai-builder

## Workflow Guideline

All work in this repository — whether human or AI driven — must be tracked
through the task management system before implementation begins. This applies
to features, fixes, refactors, and documentation. Work in `/sandbox` is
exempt; the sandbox is for unstructured experimentation.

**Before starting any work outside `/sandbox`:**
1. Check whether a task already exists for the work.
2. If not, create one using `new-task.sh` and move it to `in-progress/`.
3. Do the work.
4. Move the task to `complete/` when done.

---

## Session Status

`project/status/` contains daily session logs (`YYYY-MM-DD.md`). **At the
start of every session, read the most recent status file** to understand where
things left off — what was in progress, what decisions were made, what is
coming up next.

**Sign-off:** when the user says "sign off", write a status summary to
`project/status/YYYY-MM-DD.md` covering: work completed, work in progress,
next up, and any key decisions. This is how context survives across sessions.

**Full documentation:** [`project/README.md`](project/README.md)

---

## Task Management

All work in this repository is tracked through a structured task management
system. Before starting any work, check the task system to understand current
priorities and status.

**Full documentation:** [`project/tasks/README.md`](project/tasks/README.md)

### Summary

Tasks are organized by epic and status. Each task is a directory containing a
`README.md` that describes the work. Subtasks are subdirectories of their
parent task.

```
project/tasks/
    <epic>/
        inbox/        # raw ideas, not yet evaluated
        draft/        # being written up
        backlog/      # refined, ordered by priority — pull from here
        in-progress/  # actively being worked on
        complete/     # done and verified
        wont-do/      # explicitly decided against
```

**When picking up work:** pull from `backlog/` in top-to-bottom order.
**When starting a task:** move it to `in-progress/` using `move-task.sh`.
**When done:** run `complete-task.sh` — no `--parent` for top-level tasks, add `--parent` for subtasks.

**To show outstanding work** (draft + backlog + in-progress, excluding complete):
```bash
project/tasks/scripts/list-tasks.sh --epic main --folder draft --depth 2
project/tasks/scripts/list-tasks.sh --epic main --folder backlog --depth 2
project/tasks/scripts/list-tasks.sh --epic main --folder in-progress --depth 2
```
Do NOT use `list-tasks.sh --epic main` without `--folder` when the user asks for
outstanding or incomplete tasks — it includes `complete/` which adds noise.

> **Rule:** Before beginning any task or subtask, describe its purpose and
> list all subtasks in order. If the project manager is human, wait for their
> approval before starting any implementation work.

> **Rule:** Always use the scripts to manage tasks. Never manually edit task
> `README.md` files to add or remove subtasks, and never manually move task
> directories between status folders. The scripts keep the filesystem and
> documentation in sync.

> **Rule:** When a subtask is finished, always run `complete-task.sh --parent`
> to mark it `[x]` before moving on to the next subtask.

> **Rule:** Subtask `Status` is binary — only `—` (not done) or `complete`
> (done). Subtasks do not have statuses like `draft`, `backlog`, or
> `in-progress`; those apply only to top-level tasks.

> **Rule:** When testing a new feature, leave the test task in place after
> verification. Move it to `complete/` using `move-task.sh` rather than
> deleting it. Test tasks serve as living examples of correct usage.

### Scripts

Run from the repo root:

```bash
project/tasks/scripts/new-task.sh       --epic main --folder draft --name <task>
project/tasks/scripts/new-task.sh       --epic main --folder draft --parent <task> --name <subtask>
project/tasks/scripts/move-task.sh      --epic main --name <task> --from <status> --to <status>
project/tasks/scripts/complete-task.sh  --epic main --folder <status> --name <task>
project/tasks/scripts/complete-task.sh  --epic main --folder <status> --parent <task> --name <subtask>
project/tasks/scripts/show-task.sh      --epic main --folder <status> --name <task>
project/tasks/scripts/delete-task.sh    --epic main --folder <status> --name <task>
project/tasks/scripts/restore-task.sh   --epic main --folder <status> --name <task>
project/tasks/scripts/list-tasks.sh     --epic main [--folder <status>] [--depth <n>] [--root <path>] [--all] [--tag <tag>]
```

