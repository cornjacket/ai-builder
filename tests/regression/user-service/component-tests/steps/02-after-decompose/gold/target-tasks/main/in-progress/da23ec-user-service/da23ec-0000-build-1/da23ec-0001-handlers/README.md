<!-- This file is managed by the ai-builder pipeline. Do not hand-edit. -->
# Task: handlers

## Goal

HTTP handler functions for the user CRUD API. Depends on the store package. Full API contract: POST /users — request body {"name":string,"email":string} → 201 {"id":string,"name":string,"email":string}; returns 400 {"error":string} on invalid or missing JSON body. GET /users/{id} → 200 {"id":string,"name":string,"email":string} or 404 {"error":"not found"}. PUT /users/{id} — request body {"name":string,"email":string} → 200 {"id":string,"name":string,"email":string}; returns 404 {"error":"not found"} if id absent, 400 {"error":string} on invalid JSON. DELETE /users/{id} → 204 (no body) or 404 {"error":"not found"}. All responses use Content-Type: application/json except 204. Handler constructor: NewHandler(s *store.Store) http.Handler — registers all routes on a new ServeMux using the Go 1.22+ pattern syntax (e.g. "POST /users", "GET /users/{id}") and returns the mux. Package: handlers. Output path: github.com/cornjacket/ai-builder/sandbox/user-service-output/handlers.

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
