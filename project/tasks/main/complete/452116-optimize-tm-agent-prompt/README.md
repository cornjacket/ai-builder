# Task: optimize-tm-agent-prompt

| Field       | Value         |
|-------------|---------------|
| Status | complete |
| Epic        | main      |
| Tags        | —      |
| Parent      | —    |
| Priority    | HIGH  |
| Complexity  | —             |
| Stop-after  | false         |
| Last-task   | false         |

## Goal

Reduce the cognitive load on the TM agent by replacing fragile parse-and-infer
steps with a dedicated script that returns the next incomplete subtask directly.

## Context

The TM agent currently identifies the next subtask by running `list-tasks.sh`
and parsing its output to find the next `[ ]` entry, then manually constructing
the path to that subtask's README. This is brittle — it relies on the agent
correctly interpreting list output and building a path string. A dedicated
`next-subtask.sh` script should encapsulate this logic so the TM prompt can
simply call the script and use its output directly.

## Components

_To be completed by the ARCHITECT._

## Design

_To be completed by the ARCHITECT._

## Acceptance Criteria

_To be completed by the ARCHITECT._

## Suggested Tools

_To be completed by the ARCHITECT._

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [x] [a77e9b-add-next-subtask-script](a77e9b-add-next-subtask-script/)
- [x] [c8df22-integrate-next-subtask-into-tm-prompt](c8df22-integrate-next-subtask-into-tm-prompt/)
<!-- subtask-list-end -->

## Notes

_None._
