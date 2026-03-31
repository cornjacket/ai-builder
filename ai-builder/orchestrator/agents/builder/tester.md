# agents/tester.py

`TesterAgent` — runs the test command recorded in `task.json` and maps the
exit code to a pipeline outcome.

## run(job_doc, output_dir, **kwargs)

**Inputs:**
- `job_doc: Path` — path to the task's `README.md`; `task.json` is resolved as
  a sibling (`job_doc.parent / "task.json"`)
- `output_dir: Path` — unused; present to satisfy the Protocol

**Reads:** `task.json["test_command"]` — shell command run via `subprocess.run(shell=True)`

**Returns `AgentResult` with:**
- `OUTCOME: TESTER_TESTS_PASS` — command exited 0
- `OUTCOME: TESTER_TESTS_FAIL` — command exited non-zero; stdout/stderr appended
- `OUTCOME: TESTER_NEED_HELP` — `task.json` missing, unreadable, or has no `test_command`

**Side effects:** none (read-only)

## Context dependency

None. `TesterAgent` takes no constructor arguments.
