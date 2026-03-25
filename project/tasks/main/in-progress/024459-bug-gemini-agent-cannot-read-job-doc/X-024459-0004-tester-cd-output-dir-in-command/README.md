# Task: tester-cd-output-dir-in-command

| Field       | Value |
|-------------|-------|
| Task-type   | USER-SUBTASK |
| Status | complete |
| Parent      | 024459-bug-gemini-agent-cannot-read-job-doc |

## Goal

Prepend cd <output_dir> to the TESTER test command in the orchestrator so
the command is fully self-contained.

## Notes

Commit: `847df83`

TESTER's cwd is a temp sandbox directory. Running bare "go test ./..." from
the sandbox fails (no Go module there). The orchestrator now prepends
"cd <output_dir> && " to the extracted test command so TESTER receives a
fully qualified, runnable command requiring no working-directory reasoning.
