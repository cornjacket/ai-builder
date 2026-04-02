# Task: reset-copies-source-to-sandbox

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | b9529c-doc-pipeline/b9529c-0009-doc-platform-monolith-regression-test             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Write `tests/regression/doc-platform-monolith/reset.sh`, which copies the
source template to `sandbox/doc-platform-monolith-output/` ready for a
pipeline run.

## Context

Mirror the logic from `doc-user-service/reset.sh` with these differences:

- Source template: `tests/regression/doc-platform-monolith/source/`
- Output sandbox: `sandbox/doc-platform-monolith-output/`
- Target task tree: `sandbox/doc-platform-monolith-target/`
- Sanity check: verify the two retained `.md` files
  (`internal/iam/README.md`, `internal/metrics/README.md`) exist in the
  template before copying (fail loudly if either is missing — they must not
  be stripped accidentally).
- Sanity check: verify NO other `.md` files are in the template (to catch
  accidental re-introduction of stripped docs).

The reset script creates the task tree from scratch each run: USER-TASK
`doc-platform-monolith` and PIPELINE-SUBTASK `doc-1` with `Level: TOP`.
Goal/Context are read from `doc-spec.md` and written to the task READMEs.
`current-job.txt` points at the `doc-1` README.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
