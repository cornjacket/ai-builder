# Task: list-tasks-by-category

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status | in-progress |
| Epic        | main               |
| Tags        | —               |
| Priority    | HIGH           |
| Category    | task-tooling           |
| Created     | 2026-05-02            |
| Completed   | —                      |
| Next-subtask-id | 0004 |

## Goal

Add category-aware views to `project/tasks/scripts/list-tasks.sh` so an
operator can answer "what's the next task I can pull for worktree X?" and
"what outstanding work clusters in which category?" without reading every
README.

Two new flags:

- `--category <branch>` — filter to tasks whose `Category:` field equals the
  given worktree-class branch (e.g. `--category task-tooling`).
- `--group-by-category` — within each status folder, group tasks by category
  and list each group on its own. Combines with `--sort-priority` to sort
  HIGH→MED→LOW→unset within each group.

Both flags should be additive to the existing `--folder`, `--depth`,
`--tag`, `--all`, and `--sort-priority` options. Tasks missing a `Category:`
or with `Category: —` should fall into a trailing `(unclassified)` group.

## Context

`Category:` was added as a required USER-TASK field in commit `d442bd0`
(task `4a8789-0000-add-category-flag-to-new-user-task`) and maps every
top-level task to one of the worktree classes in
[`project/tasks/classes.md`](../../../classes.md). The whole point of the
category was to enable parallel work in independent worktrees.

The current `list-tasks.sh` reads `Priority` (line 77 — `get_priority`) but
ignores `Category` entirely. To unblock parallel implementation, an operator
needs to pull the next backlog item *for a specific worktree class* — today
that requires opening every README in `backlog/` and skimming the field by
hand.

This task is HIGH priority because it gates parallel-worktree scheduling:
without category-aware listing, picking work for `gemini-compat`,
`orchestrator-core`, etc. is manual and error-prone.

The Category-only field lives in the table as `| Category    | <value> |`.
Subtasks inherit category from their parent and don't carry the field
themselves, so category logic only applies at the top-level task layer
(depth-1 view); deeper recursion continues to use existing rules.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [x] [X-8ec43a-0000-add-category-filter-flag](X-8ec43a-0000-add-category-filter-flag/)
- [x] [X-8ec43a-0001-add-group-by-category-flag](X-8ec43a-0001-add-group-by-category-flag/)
- [ ] [8ec43a-0002-add-bats-tests](8ec43a-0002-add-bats-tests/)
- [ ] [8ec43a-0003-update-claude-md-and-companion-doc](8ec43a-0003-update-claude-md-and-companion-doc/)
<!-- subtask-list-end -->

## Notes

_None._
