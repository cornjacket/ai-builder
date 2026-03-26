<!-- This file is managed by the ai-builder pipeline. Do not hand-edit. -->
# Task: build-1

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
