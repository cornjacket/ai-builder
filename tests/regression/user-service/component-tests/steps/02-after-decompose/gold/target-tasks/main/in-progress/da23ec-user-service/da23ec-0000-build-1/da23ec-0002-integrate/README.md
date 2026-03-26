<!-- This file is managed by the ai-builder pipeline. Do not hand-edit. -->
# Task: integrate

## Goal

Wire store and handlers into the service entry point. Write main.go at the output root (github.com/cornjacket/ai-builder/sandbox/user-service-output). Initialise a store.Store, pass it to handlers.NewHandler, and start an http.Server listening on :8080. Write go.mod with module path github.com/cornjacket/ai-builder/sandbox/user-service-output and Go 1.22 (minimum needed for enhanced ServeMux routing). End-to-end acceptance criteria: (1) POST /users with valid JSON body returns 201 and a JSON user object with a non-empty id field; (2) GET /users/{id} with the returned id returns 200 and the same user; (3) GET /users/{nonexistent-id} returns 404; (4) PUT /users/{id} with updated fields returns 200 with updated values; (5) DELETE /users/{id} returns 204; (6) GET /users/{id} after deletion returns 404; (7) server listens on port 8080.

## Context

### Level 1 — da23ec-0000-build-1
_To be written._

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
