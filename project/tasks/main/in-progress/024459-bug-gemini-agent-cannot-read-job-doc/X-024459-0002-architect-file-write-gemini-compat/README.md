# Task: architect-file-write-gemini-compat

| Field       | Value |
|-------------|-------|
| Task-type   | USER-SUBTASK |
| Status | complete |
| Parent      | 024459-bug-gemini-agent-cannot-read-job-doc |

## Goal

Add ARCHITECT entry to gemini_compat.py prohibiting write_file and mandating
printf via run_shell_command for documentation file writes.

## Notes

Commit: `568ae13`

Gemini's write_file tool is sandboxed to the temp cwd. ARCHITECT writes .md
documentation files to the output directory (an absolute path outside the
sandbox). Fix: add ARCHITECT section to gemini_compat.py with the same
printf-via-run_shell_command rule already used for IMPLEMENTOR.
