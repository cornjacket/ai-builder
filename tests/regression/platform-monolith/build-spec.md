<!-- This file is managed by the ai-builder pipeline. Do not hand-edit. -->
# Task: build-1

## Goal

Build a networked monolith platform in Go. A networked monolith is a single
process with a single binary entry point (`cmd/platform/main.go`). The single
process starts two HTTP listeners on separate ports — one for metrics ingestion
and one for IAM. There is exactly one `main` package and one binary.

**Metrics listener (port 8081)**

Records frontend user interaction events.

API:
- `POST /events` — record an event; body: `{"type": "click-mouse"|"submit-form", "userId": "<string>", "payload": {}}` → 201 with event object (includes generated `id`)
- `GET /events`  — list all recorded events → 200 with JSON array

**IAM listener (port 8082)**

Identity and access management. Internally composed of two logical components:
(a) user authentication and lifecycle, and (b) authorisation/RBAC.

API:
- User lifecycle:
  - `POST /users`        — register user; body: `{"username": "<string>", "password": "<string>"}` → 201 with user object (includes `id`, no password in response)
  - `GET /users/{id}`    — get user by ID → 200 or 404
  - `DELETE /users/{id}` — delete user → 200/204 or 404
- Authentication:
  - `POST /auth/login`   — authenticate; body: `{"username": "<string>", "password": "<string>"}` → 200 with token object (includes `token` field)
  - `POST /auth/logout`  — invalidate token; header: `Authorization: Bearer <token>` → 200/204
- RBAC:
  - `POST /roles`             — create role; body: `{"name": "<string>", "permissions": ["<string>"]}` → 201 with role object (includes `id`)
  - `GET /roles`              — list roles → 200 with JSON array
  - `POST /users/{id}/roles`  — assign role to user; body: `{"roleId": "<string>"}` → 200/201
  - `GET /users/{id}/roles`   — list user's roles → 200 with JSON array
  - `POST /authz/check`       — check permission; body: `{"userId": "<string>", "permission": "<string>"}` → 200 with `{"allowed": <bool>}`

## Context

This is a regression test for the ai-builder multi-level decomposition pipeline.
The platform is a networked monolith: one process, one binary, two listeners.
The IAM listener is itself internally composed of two components (auth-lifecycle
and authz-rbac). The pipeline must traverse this multi-level tree, implementing
and testing each level before walking up to integrate the next.

**Language:** Go
**Binary:** single binary — the only `main` package in the entire codebase
must be `cmd/platform/main.go`. There must be no other `main` packages.
Component-level implementations must not create their own `cmd/` directories
or standalone binaries. `cmd/platform/main.go` starts both listeners.
**Storage:** in-memory (no database required)
**Testing requirements:**
- Unit tests at each functional level (each atomic component must have unit tests)
- End-to-end acceptance tests at each integrate step:
  - INTERNAL integrate: verify the component's contract against its API;
    do not create a standalone binary — use `net/http/httptest` or similar
  - TOP integrate (this task): create `cmd/platform/main.go` as the sole
    binary entry point; start both listeners and verify all endpoints pass

## Components

_To be completed by the ARCHITECT._

## Design

_To be completed by the ARCHITECT._

## Acceptance Criteria

_To be completed by the ARCHITECT._

## Test Command

_To be completed by the ARCHITECT._

## Suggested Tools

_To be completed by the ARCHITECT._

## Notes

_None._
