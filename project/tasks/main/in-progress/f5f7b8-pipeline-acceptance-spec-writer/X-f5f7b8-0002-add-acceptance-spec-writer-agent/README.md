# Task: add-acceptance-spec-writer-agent

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

Create the ACCEPTANCE_SPEC_WRITER agent: a Claude-powered stage that reads the
build spec and produces `acceptance-spec.md` and `acceptance-spec.json` in the
output directory before any ARCHITECT runs.

## Context

The agent reads `## Goal` and `## Context` from the build spec (job doc). It
extracts HTTP endpoints verbatim — field names, status codes, request/response
schemas — and writes:
- `acceptance-spec.md` — human-readable, copied verbatim from the spec
- `acceptance-spec.json` — machine-readable, conforming to the schema defined
  in `f5f7b8-0001-define-acceptance-spec-format`

If the build spec contains non-HTTP interfaces, the agent must halt with an
error: state which interface was detected, that only HTTP is supported, and that
a new acceptance spec schema must be defined first.

Both files are written to a known path in the output dir. Downstream ARCHITECTs
read them by convention — no orchestrator injection needed.

Deliverables:
- `ai-builder/orchestrator/agents/builder/acceptance-spec-writer.py` (or `.sh`)
- `ai-builder/orchestrator/agents/builder/acceptance-spec-writer.md` — companion doc

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
