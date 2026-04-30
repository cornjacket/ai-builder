# Task: implementor-prompt-inlined-content

| Field       | Value |
|-------------|-------|
| Task-type   | USER-SUBTASK |
| Status | complete |
| Parent      | 024459-bug-gemini-agent-cannot-read-job-doc |

## Goal

Update IMPLEMENTOR role prompt to reference inlined content rather than
directing the agent to read the job document.

## Notes

Commit: `1246a80`

roles/IMPLEMENTOR.md said "Read the Design section of the job document."
Since Design, AC, and Test Command are all inlined into the prompt by the
orchestrator, this instruction is both unnecessary and misleading. Updated to:
"The Design, Acceptance Criteria, and Test Command have been provided directly
in your prompt."
