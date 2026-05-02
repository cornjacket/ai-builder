# Task: add-group-by-category-flag

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status      | —                      |
| Epic        | main               |
| Tags        | —               |
| Parent      | 8ec43a-list-tasks-by-category             |
| Priority    | —           |
| Created     | 2026-05-02            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

Add `--group-by-category` to `list-tasks.sh`. When set, within each status
folder tasks are grouped by `Category:` value with each group printed under
a `[<category>]` sub-heading. Tasks lacking a Category fall into a trailing
`(unclassified)` group.

Combines with `--sort-priority` to order tasks HIGH→MED→LOW→unset within
each category group. Combines with `--category` to do a single-category
view (in which case the grouping is trivially one group, but the flag
still prints the category sub-heading for consistency).

## Context

Group order: classes 1–8 in the order they appear in `classes.md`
(branches: gemini-compat, orchestrator-core, acceptance-spec,
new-pipelines, regression-infra, task-tooling, docs, workspace-mgmt),
then `unclassified`. Hard-code the order list at the top of the script —
parsing classes.md adds complexity for no gain.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
