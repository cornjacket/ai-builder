# Task: verify-gold-tests

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | f5f7b8-pipeline-acceptance-spec-writer             |
| Priority    | —           |
| Created     | 2026-04-04            |
| Completed | 2026-04-05 |
| Next-subtask-id | 0000               |

## Goal

Run the `8985d4-platform-monolith` regression and confirm that the five IAM API
gold test failures that motivated this task no longer occur.

## Context

The root cause (task f5f7b8) was ARCHITECT drift during the IAM API build:
- `roleId` → `role_id`, `userId` → `user_id`, `permission` → `role`
- `GET /roles` omitted from acceptance criteria
- `DELETE /roles/{id}` invented (not in spec)
- Status codes changed (spec: 200/201, ARCHITECT: 204)

The pipeline's own TESTER passed because it tested against the drifted criteria.
Only the human-authored gold tests caught it.

This subtask verifies the fix end-to-end: run the full regression, check that
all five previously-failing gold tests now pass, and confirm no new failures
were introduced.

Requires subtasks 0001–0005 to be complete before running.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
