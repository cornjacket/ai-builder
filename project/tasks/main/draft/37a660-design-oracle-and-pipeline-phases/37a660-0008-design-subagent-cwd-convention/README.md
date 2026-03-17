# Subtask: design-subagent-cwd-convention

| Field    | Value                |
|----------|----------------------|
| Status   | —                    |
| Epic     | main             |
| Tags     | oracle, orchestrator, claude-md             |
| Parent   | 37a660-design-oracle-and-pipeline-phases           |
| Priority | MED         |

## Description

The CLAUDE.md hierarchy only loads correctly if subagents are spawned in the
right working directory. Instructing an already-running agent to "go work in
`tests/system-tests/`" does NOT trigger a re-scan — the CWD at launch
determines what gets loaded.

This means the orchestrator must have an explicit convention for what CWD to
use when spawning each role (ARCHITECT, IMPLEMENTOR, TESTER).

**Questions to resolve:**

- What CWD should each role be spawned with? Options:
  - Always the target repo root (simplest, loses subdirectory CLAUDE.md context)
  - The directory most relevant to the subtask being worked on (correct, but
    requires the TM to record the relevant path in the job document)
  - The deepest common ancestor of all paths the subtask touches
- How does the TM communicate the intended CWD to the orchestrator?
  Should the job document include an explicit `Working directory:` field?
- Should the orchestrator validate that the CWD exists before spawning?
- Does the ARCHITECT need a different CWD than the IMPLEMENTOR for the
  same subtask? (ARCHITECT may need repo root to see the full picture;
  IMPLEMENTOR may benefit from a narrower CWD)

**Deliverables:**
- A defined convention for CWD per role, documented in the orchestrator
- Any required changes to the job document format to carry CWD information
- Notes in `roles/TASK_MANAGER.md` on how the TM should specify CWD

## Notes

Example: spawning TESTER with `cwd=/app/tests/system-tests` loads:
  `system-tests/CLAUDE.md` + `tests/CLAUDE.md` + `app/CLAUDE.md` ✓

Spawning TESTER with `cwd=/app` and instructing it to work in
`tests/system-tests` loads only `app/CLAUDE.md` — the subdirectory
CLAUDE.md files are never seen. ✗
