# Task: port-log-md-update-emoji-rule

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | in-progress             |
| Epic        | main               |
| Tags        | —               |
| Priority    | MED           |
| Category    | task-tooling           |
| Created     | 2026-04-30            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

Port the `📝 log.md updated` chat-announcement directive from
`ai-engineering-sandbox/document-analyzer/CLAUDE.md` into this repo's
`CLAUDE.md`, and fold the same guidance (plus the entry-format and
back-fill rules already in our CLAUDE.md) into
`ai-builder-lessons/lessons/038-work-log-at-task-granularity.md` so the
generalised lesson reflects what we actually do here.

## Context

We adopted lesson 038's work-log mechanism in commit `69acb01`, but the
companion rule that document-analyzer uses — having Claude announce
log.md edits in chat with a literal `📝 log.md updated` line — was never
ported. Without it, log edits are invisible inside long tool-call
sequences; the user noticed today that they couldn't see the marker
they expected.

This task ports the rule into `ai-builder/CLAUDE.md`'s `## Work Log`
section and updates lesson 038 to incorporate both the announcement
directive and the entry-format / helper-script details that live in our
CLAUDE.md but were absent from the lesson, so the lesson stands alone
as the reference.

Cross-repo: the lesson edit lives in `ai-builder-lessons` and is
committed and pushed there separately.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
