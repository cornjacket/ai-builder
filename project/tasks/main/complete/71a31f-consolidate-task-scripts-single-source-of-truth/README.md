# Task: consolidate-task-scripts-single-source-of-truth

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Priority    | HIGH           |
| Created     | 2026-04-02            |
| Completed | 2026-04-02 |
| Next-subtask-id | 0000               |

## Goal

Eliminate the duplicate copy of task management scripts in `target/project/tasks/scripts/`
by making `setup-project.sh` copy from `project/tasks/scripts/` directly. One source of
truth; changes to the canonical scripts are automatically picked up by all regression tests
on the next `reset.sh` run.

## Context

`target/setup-project.sh` currently does `cp -r target/project/ <target-repo>/project/`,
which means `target/project/tasks/scripts/` is an independent copy of the canonical
`project/tasks/scripts/`. Every change to the canonical scripts must be manually ported.
This has already caused silent drift: `reorder-subtasks.py` was never ported, and the new
`Created`/`Completed` timestamp fields were missing from the target copy until caught manually.

There are 5 regression test sandbox targets plus the top-level `target/` itself — all
containing stale copies.

**Changes required:**
- Update `target/setup-project.sh` to copy scripts from `$REPO_ROOT/project/tasks/scripts/`
  instead of `$SCRIPT_DIR/project/tasks/scripts/`
- Delete `target/project/tasks/scripts/` and all its contents
- Keep the `target/project/` skeleton: `.gitkeep` files for the epic status dirs and
  `project/status/.gitkeep` — these have no equivalent in `project/tasks/scripts/`
- Verify all regression test `reset.sh` scripts still work after the change

## Notes

`setup-project.sh` needs `REPO_ROOT` — derive it as one level up from `target/`:
`REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"`
