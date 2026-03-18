# Task: document-monitoring-design

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 51de6e-track-pipeline-build-metrics             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Write `ai-builder/orchestrator/monitoring.md` — a design document covering the
pipeline monitoring architecture and its intended evolution.

Sections to include:

1. **Design principles** — orchestrator owns all monitoring; agents are
   unaware; data flows out, not in; clean function boundary for future
   persistence.

2. **What is captured** — per-invocation timing, token usage (in/out/cached),
   outcomes, description derived from job path.

3. **Live execution log** — how the `## Execution Log` section in the
   Level: TOP pipeline-subtask README is updated after each invocation;
   how to interpret it during a run.

4. **End-of-run outputs** — `run-summary.md` and `run-metrics.json` in the
   output directory; section-by-section description of each, including the
   per-agent invocation count table (useful when a run mixes claude and gemini).

5. **Extension points** — how to add database persistence or a dashboard:
   replace or wrap the `metrics.py` functions; the `InvocationRecord` and
   `RunData` dataclasses are the contract.

6. **Gemini and other agents** — token fields default to zero for non-claude
   agents; the rest of the metrics still work.

Also add `monitoring.md` to the file index in `ai-builder/orchestrator/README.md`.

## Context

The ai-builder/ directory is where design decisions and behavioral contracts
live. This document is for future contributors (human or AI) who need to
understand or extend the monitoring system without reading the source code.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
