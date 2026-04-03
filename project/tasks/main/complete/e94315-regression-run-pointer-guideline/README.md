# Task: regression-run-pointer-guideline

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Created     | 2026-04-03            |
| Completed | 2026-04-03 |
| Next-subtask-id | 0000               |

## Goal

Document the convention for recording regression run pointers in user-task
READMEs, and create `tests/regression/CLAUDE.md` to hold operational
guidelines for running regressions.

## Context

Currently there is no pointer from a user-task in `project/tasks/` to the
sandbox regression it triggered. To find a run you have to know the sandbox
convention and go searching — there's nothing in the task you're already
looking at.

The fix: establish a workflow rule that after `reset.sh` and before running
the pipeline, the operator records sandbox paths and the pipeline task ID in
the subtask README under a `## Run` section:

```markdown
## Run

| Field | Value |
|---|---|
| Run date | 2026-04-03 |
| Target | `sandbox/regressions/<name>/target/` |
| Output | `sandbox/regressions/<name>/output/` |
| Pipeline task | `<hex-id>-<name>` |
```

This guideline belongs in `tests/regression/CLAUDE.md` (scoped to regression
work, not loaded in every session) rather than the top-level `CLAUDE.md`.

`tests/regression/README.md` covers the human-readable description of the
regression suite structure — the operational workflow guideline for Claude
goes in `CLAUDE.md` only.

## Notes

- Create `tests/regression/CLAUDE.md`.
- Create `tests/regression/GEMINI.md` as a symlink to `CLAUDE.md`.
- No script changes needed — this is a workflow/documentation convention.
- Apply the convention retroactively to any in-progress regression subtasks
  when picking them up.
