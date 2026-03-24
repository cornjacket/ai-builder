# Task: redesign-pipeline-communication-architecture

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | in-progress             |
| Epic        | main               |
| Tags        | orchestrator, architecture, pipeline               |
| Priority    | HIGH           |
| Next-subtask-id | 0000               |

## Goal

Redesign the pipeline's communication architecture so that agents communicate
through a single structured channel (prose + terminal JSON block) rather than
the current mix of disk file writes, regex-parsed response text, and JSON.

## Context

The pipeline evolved incrementally from a human task management system, causing
pipeline tasks to inherit Markdown as their format even though machines need
structured data. The result is three incoherent communication channels in use
simultaneously:

- ARCHITECT writes a `## Components` Markdown table to README.md on disk;
  DECOMPOSE_HANDLER parses it back with regex
- Outcomes and handoffs travel through response text parsed with regex
- Completion state lives in `task.json` as JSON

The proposed direction: agents emit prose followed by a fenced JSON block
containing all machine-readable output (outcome, handoff, components, design,
documents). The orchestrator parses the JSON block; prose streams in real time
for observability. Pipeline task state moves to pure JSON; README.md for
pipeline tasks becomes a generated view, not the authoritative record.

## Notes

Brainstorm: `sandbox/brainstorm-pipeline-communication-architecture.md`

This is a significant multi-task initiative. Subtasks to be defined once the
brainstorm is sufficiently resolved.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
