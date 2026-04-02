# Task: enforce-no-regression-without-permission

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Update `CLAUDE.md` and `target/init-claude-md.sh` to make the no-regression-
without-explicit-permission rule visible to both the Oracle (this repo) and
pipeline agents (target repos), so it is enforced consistently.

## Context

`CLAUDE.md` already states the rule ("Never start a regression run without
explicit user approval") but `init-claude-md.sh` generates the `CLAUDE.md`
written into target repos for pipeline agents. If that generated file does not
carry the same rule, an agent operating inside a target repo could start a
regression run without realising it is prohibited.

Changes required:
- Review `target/init-claude-md.sh` — if the generated `CLAUDE.md` omits the
  regression rule, add it.
- Confirm the rule in this repo's `CLAUDE.md` is unambiguous: no regression
  without an explicit instruction in the current user message.
- Consider whether the rule should also appear in the orchestrator's own
  `README.md` under a "Safety" or "Operating Rules" section so it is visible
  to anyone reading the orchestrator docs.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
