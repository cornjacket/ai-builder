# Task: tester-internal-handler

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 49352f-redesign-pipeline-communication-architecture             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Replace the TESTER AI agent with an internal Python handler that runs the test
command via `subprocess.run()`, checks the exit code, and returns a structured
result. Eliminate the AI invocation for the common pass/fail case.

## Context

TESTER's job is entirely mechanical: run a shell command, check the exit code,
return pass or fail. No AI judgment is required. The current AI agent wastes a
full invocation on a task that a Python subprocess handles completely. The test
command is already available in `task.json` from ARCHITECT (subtask 0004), so
the handler needs no file reads.

**Implementation:**
```python
def _run_tester_internal(test_command: str, output_dir: Path) -> AgentResult:
    proc = subprocess.run(test_command, shell=True, capture_output=True, text=True)
    if proc.returncode == 0:
        response = "OUTCOME: TESTER_TESTS_PASS\nHANDOFF: All tests passed."
    else:
        response = (
            f"OUTCOME: TESTER_TESTS_FAIL\n"
            f"HANDOFF: Tests failed.\n{proc.stdout}\n{proc.stderr}"
        )
    return AgentResult(exit_code=0, response=response)
```

On failure, the full test output is included in the handoff so IMPLEMENTOR can
act on it — no AI needed to interpret the exit code.

**Exception path — `TESTER_NEED_HELP`:** if `subprocess.run()` raises an
exception (missing binary, broken environment), the handler emits
`TESTER_NEED_HELP` to trigger human intervention. This is the only case where
the old AI TESTER added value.

**Test command source:** read from `task.json` `test_command` field (set by
ARCHITECT in subtask 0004). The command already includes `cd <output_dir> &&`
from the orchestrator (carried forward from the existing behavior).

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
