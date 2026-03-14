# Subtask: 702059-add-start-role-flag-to-orchestrator

| Field    | Value                |
|----------|----------------------|
| Status | wont-do |
| Epic        | main             |
| Tags        | —             |
| Parent      | 8eea17-implement-decomposition-in-orchestrator           |
| Priority    | —         |
| Complexity  | —                    |
| Stop-after  | false                |

## Description

Add a `--start-role <ROLE>` flag to `ai-builder/orchestrator/orchestrator.py`
to allow the caller to override the default starting role (currently always
`ARCHITECT`).

Use cases:
- Resume a halted pipeline from a specific role without re-running earlier stages
- Run a single role in isolation against a known job document
- Iterate on a role's prompt during development

The flag should validate that the requested role exists in `AGENTS` and be
compatible with both TM and non-TM mode. See the original design in
`project/tasks/main/draft/702059-add-start-role-flag-to-orchestrator/`.

## Notes

The pipeline already always starts at ARCHITECT by default (fixed as part of
`8eea17`). This flag is an enhancement for resume and targeted testing use
cases.
