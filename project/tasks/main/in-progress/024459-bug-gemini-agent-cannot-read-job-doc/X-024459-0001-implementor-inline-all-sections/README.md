# Task: implementor-inline-all-sections

| Field       | Value |
|-------------|-------|
| Task-type   | USER-SUBTASK |
| Status | complete |
| Parent      | 024459-bug-gemini-agent-cannot-read-job-doc |

## Goal

Inline Goal, Context, Design, Acceptance Criteria, and Test Command directly
into the IMPLEMENTOR prompt so the agent never calls read_file.

## Notes

Commit: `568ae13`

Orchestrator `build_prompt()` for IMPLEMENTOR: iterates over all required
sections, extracts each via regex, and inlines them into the prompt. Context
(ancestry chain) included so IMPLEMENTOR has full lineage without reading files.
