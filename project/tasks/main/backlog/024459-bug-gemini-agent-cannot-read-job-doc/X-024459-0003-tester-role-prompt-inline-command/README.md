# Task: tester-role-prompt-inline-command

| Field       | Value |
|-------------|-------|
| Task-type   | USER-SUBTASK |
| Status | complete |
| Parent      | 024459-bug-gemini-agent-cannot-read-job-doc |

## Goal

Update TESTER role prompt to use the inlined test command from the prompt
rather than reading it from the job document.

## Notes

Commit: `88831b8`

roles/TESTER.md step 1 said "Read the ## Test Command section from the job
document". Gemini called read_file, hit sandbox error, and wandered for minutes
before emitting TESTER_NEED_HELP. The test command is already inlined in the
prompt by the orchestrator. Updated step 1 to use the inlined command directly.
