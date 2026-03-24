# Task: implement-prompt-template-variable-injection

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status | wont-do |
| Epic        | main               |
| Tags        | orchestrator, prompts |
| Priority    | MED                   |
| Next-subtask-id | 0000               |
## Goal

Implement a template variable injection system so that handler prompts
(`DECOMPOSE_HANDLER`, `LEAF_COMPLETE_HANDLER`) can be defined as static
files rather than generated in Python, completing the `--state-machine`
vision from `2faff3-add-configurable-start-state-and-routes-to-orchestrator`.

## Context

In `2faff3`, the `--state-machine` feature allows roles to declare a
`"prompt"` file path in the machine JSON. For most roles (ARCHITECT,
IMPLEMENTOR, TESTER) this works today — their prompts are already static
markdown files. The two handler roles are the exception:

- `DECOMPOSE_HANDLER` — prompt is built in Python with runtime variables:
  `TARGET_REPO`, `EPIC`, `PM_SCRIPTS_DIR`, `output_dir`, `current_job_path`
- `LEAF_COMPLETE_HANDLER` — same runtime variables

Because of this, `2faff3` uses `"prompt": null` for these roles and falls
back to Python-generated prompts. This means the machine file cannot be
fully self-contained — two roles still require hardcoded Python logic.

This task implements a `{{VAR}}` substitution system for prompt files:
the orchestrator substitutes known runtime values into prompt file content
before passing it to the agent. Known variables at prompt-build time:

| Variable | Value |
|----------|-------|
| `{{TARGET_REPO}}` | `--target-repo` CLI value |
| `{{EPIC}}` | `--epic` CLI value |
| `{{PM_SCRIPTS_DIR}}` | derived from `TARGET_REPO` |
| `{{OUTPUT_DIR}}` | `--output-dir` CLI value |
| `{{CURRENT_JOB_PATH}}` | read from `current-job.txt` at call time |

Once implemented, the handler prompt files can be extracted from Python
into `roles/DECOMPOSE_HANDLER.md` and `roles/LEAF_COMPLETE_HANDLER.md`,
and their `"prompt": null` entries in the machine file replaced with the
file paths. The Python prompt-generation fallback for these roles can then
be deleted.

**Prerequisite:** `2faff3-add-configurable-start-state-and-routes-to-orchestrator`
must be complete before this task is meaningful.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

### Obsolete — superseded by handler internalization

Both DECOMPOSE_HANDLER and LEAF_COMPLETE_HANDLER were made internal Python
functions (zero tokens, no prompt) as part of
`829461-split-task-format-and-internalize-decompose-handler`. Since neither
handler invokes an AI agent anymore, there is no prompt to extract or
template — the problem this task was solving no longer exists.
