# Task: resolve-task-manager-and-documenter-role-files

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 46f78a-stage-builder-machine-as-configurable-pipeline             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Decide what happens to `roles/TASK_MANAGER.md` before the structural
reorganisation begins. All other `roles/` files have settled fates:

| File | Decision |
|------|----------|
| `roles/DOCUMENTER.md` | Guidelines section → `docs/guidelines/documentation-standards.md`; role wrapper retired |
| `roles/doc-format.md` | → `docs/guidelines/doc-format.md` |
| `roles/TESTER.md` | Retire — redundant with `agents/builder/tester.md` and `agent-roles.md` |
| `roles/ARCHITECT.md` | → `machines/builder/roles/ARCHITECT.md` |
| `roles/IMPLEMENTOR.md` | → `machines/builder/roles/IMPLEMENTOR.md` |

## Context

**`roles/TASK_MANAGER.md`**

Describes the Oracle/human TM role — decomposing work, sequencing tasks,
driving the pipeline. It was never a pipeline agent prompt; it is a reference
document for the human operator. It has no references in any machine JSON.

Options:
- **Move to `ai-builder/docs/`** as an operator/process guide — closest to
  where other ai-builder process docs live
- **Move to `project/`** as it describes Oracle behaviour, which is a
  project-level concern
- **Retire** if the content is now covered by `CLAUDE.md`

Skim CLAUDE.md and TASK_MANAGER.md, make the call, record it in the Notes
section below, then proceed to subtask 0001.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

**Revised decision: Retire `roles/TASK_MANAGER.md`, inline valuable content into `CLAUDE.md`**

`TASK_MANAGER.md` was written as an AI agent prompt for when TM was an AI agent.
That role no longer exists — TM is now the Oracle (human operator). The content
that was AI-agent instruction is either stale or already implicit in CLAUDE.md.

However, three sections contain genuine operator guidance not currently in CLAUDE.md:
- **Task granularity rules** — ~5 files / ~3 concerns heuristics for when to split tasks
- **TESTER failure decision rules** — bug in code vs. requirement misunderstood vs. systemic issue vs. flaky
- **When to break down vs. proceed as one task**

These belong in CLAUDE.md's Task Management section (not in a separate doc),
since CLAUDE.md is the Oracle's reference. Subtask 0002 handles the inline + deletion.
