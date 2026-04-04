# Task: add-test-support-for-gemini-subagents

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status | in-progress |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Category    | gemini-compat          |
| Next-subtask-id | 0006 |

## Goal

Add comprehensive support and testing for Gemini subagents within the orchestrator. This includes resolving issues related to token usage reporting, ensuring correct parsing of Gemini's `stream-json` output, and validating overall compatibility with the existing pipeline architecture.

## Context

During previous attempts to integrate Gemini agents, several issues arose:
- The orchestrator's token tracking was not fully compatible with Gemini's `stream-json` output format, specifically the `stats` field in the `result` event.
- The `parse_outcome` function in `orchestrator.py` was susceptible to split `OUTCOME:` values due to how Gemini streamed its responses, leading to incorrect state transitions.
- The `agent_wrapper.py` needed modifications to correctly handle Gemini's CLI invocation and its output events.
- Initial attempts to set the working directory for Gemini agents were problematic, leading to agents searching irrelevant paths.

This task aims to systematically address these issues, implement robust solutions, and verify the correct functioning of Gemini subagents through dedicated testing.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [x] [X-e62647-0000-document-gemini-stream-json-format](X-e62647-0000-document-gemini-stream-json-format/)
- [x] [X-e62647-0001-update-agent-wrapper-for-gemini](X-e62647-0001-update-agent-wrapper-for-gemini/)
- [x] [X-e62647-0002-add-gemini-machine-files](X-e62647-0002-add-gemini-machine-files/)
- [x] [X-e62647-0003-fix-gemini-cwd-isolation](X-e62647-0003-fix-gemini-cwd-isolation/)
- [x] [X-e62647-0004-run-fibonacci-regression-with-gemini](X-e62647-0004-run-fibonacci-regression-with-gemini/)
- [ ] [e62647-0005-run-tm-regression-with-gemini](e62647-0005-run-tm-regression-with-gemini/)
<!-- subtask-list-end -->

## Notes

_None._