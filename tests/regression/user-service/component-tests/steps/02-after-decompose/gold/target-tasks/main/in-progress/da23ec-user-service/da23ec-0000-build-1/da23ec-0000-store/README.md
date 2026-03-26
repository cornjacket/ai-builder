<!-- This file is managed by the ai-builder pipeline. Do not hand-edit. -->
# Task: store

## Goal

In-memory thread-safe store for User records. User struct fields: ID string (UUID v4, assigned on create), Name string, Email string. Operations: Create(u User) User — assigns a new UUID to ID, stores the record, returns the stored record; GetByID(id string) (User, bool) — returns the record and true, or zero value and false if not found; Update(id string, u User) (User, bool) — replaces the stored record's Name and Email (preserves ID), returns updated record and true, or false if not found; Delete(id string) bool — removes the record, returns true if it existed. Must be safe for concurrent use (sync.RWMutex or sync.Map). Package: store. Output path: github.com/cornjacket/ai-builder/sandbox/user-service-output/store.

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
