# Task: user-service

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | in-progress             |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Next-subtask-id | 0001 |

## Goal
Build a user management HTTP service in Go with the following API:

- `POST /users` — create a user (JSON body), return the created user with generated ID
- `GET /users/{id}` — retrieve user by ID; return 404 if not found
- `PUT /users/{id}` — update user by ID; return 404 if not found
- `DELETE /users/{id}` — delete user by ID; return 404 if not found

Port: 8080. Response format: JSON. Storage: in-memory. No authentication.

## Context
This is a regression test for the ai-builder decomposition pipeline.
The pipeline must decompose this service into components, implement each
one, and verify the assembled service passes the acceptance criteria.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [ ] [da23ec-0000-build-1](da23ec-0000-build-1/)
<!-- subtask-list-end -->

## Notes

_None._
