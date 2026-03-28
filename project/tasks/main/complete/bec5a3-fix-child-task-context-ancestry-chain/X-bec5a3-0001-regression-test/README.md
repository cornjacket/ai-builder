# Task: regression-test

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | bec5a3-fix-child-task-context-ancestry-chain             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Run the user-service regression to verify that the depth field and ancestry
chain context are correctly written into each child subtask's task.json during
DECOMPOSE_HANDLER execution, and that the full pipeline completes cleanly.

## Context

Subtask 0000 implemented the `depth` field in task.json and the labelled
ancestry chain (`### Level N — <name>`) in child context. The regression
exercises this through a real single-level decomposition: user-service →
components. After the pipeline completes, inspect child task.json files to
confirm `depth: 1` and a `### Level 1 — <parent-name>` entry in `context`.
Also run the gold HTTP behavioural tests.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
