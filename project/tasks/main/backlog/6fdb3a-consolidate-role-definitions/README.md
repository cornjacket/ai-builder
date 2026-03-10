# Task: consolidate-role-definitions

| Field    | Value                |
|----------|----------------------|
| Status   | backlog           |
| Epic     | main             |
| Tags     | orchestrator, refactor             |
| Parent   | —           |
| Priority | MED         |

## Description

Move all pipeline role definitions into `roles/` as individual Markdown files
and update all references to them.

Currently the ARCHITECT, IMPLEMENTOR, and TESTER role definitions are inline
strings inside `ai-builder/orchestrator.py`. `roles/PROJECT_MANAGER.md`
already exists as the first properly extracted role file.

Steps:
- Extract the ARCHITECT, IMPLEMENTOR, and TESTER role strings from
  `sandbox/orchestrator/orchestrator.py` into:
  - `roles/ARCHITECT.md`
  - `roles/IMPLEMENTOR.md`
  - `roles/TESTER.md`
- Update `orchestrator.py` to load role definitions from the `roles/` directory
  at runtime instead of using inline strings
- Search the codebase for any other references to these role definitions and
  update them to point to `roles/`
- Verify the orchestrator still runs correctly after the change (use the
  Fibonacci regression test)

## Documentation

Update `sandbox/brainstorm-agentic-platform-builder-orchestration.md` references
to `roles/` if needed. None needed in `CLAUDE.md`.

## Subtasks

<!-- When a subtask is finished, run complete-subtask.sh to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

Role definitions are currently at lines 46–70 of
`ai-builder/orchestrator.py` as a `ROLE_PROMPTS` dict.
