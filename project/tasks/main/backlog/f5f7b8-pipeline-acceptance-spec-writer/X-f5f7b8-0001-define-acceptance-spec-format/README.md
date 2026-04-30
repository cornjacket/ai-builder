# Task: define-acceptance-spec-format

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | f5f7b8-pipeline-acceptance-spec-writer             |
| Priority    | —           |
| Created     | 2026-04-04            |
| Completed | 2026-04-04 |
| Next-subtask-id | 0000               |

## Goal

Define and document the `acceptance-spec.json` schema that ACCEPTANCE_SPEC_WRITER
produces and the spec coverage checker consumes. Write a JSON Schema file and a
short spec format guide that build spec authors can follow.

## Context

The schema is HTTP-only (v1): an array of endpoints, each with `method`, `path`,
and `status_codes[]`. See `sandbox/brainstorms/brainstorm-acceptance-spec-json-schema.md`
for the full decision record.

If ACCEPTANCE_SPEC_WRITER detects interfaces other than HTTP, it must halt the
pipeline with an error telling the user: (1) which interface type was detected,
(2) that the builder pipeline only supports HTTP, (3) that a new acceptance spec
schema must be defined before this build spec can be run.

Deliverables:
- `ai-builder/orchestrator/agents/builder/acceptance-spec-schema.json` — JSON Schema
- `ai-builder/orchestrator/agents/builder/acceptance-spec-format.md` — human-readable
  format guide for build spec authors

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
