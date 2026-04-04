# Task: review-pipeline

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | pipeline, review               |
| Priority    | MED           |
| Category    | new-pipelines          |
| Next-subtask-id | 0000               |

## Goal

Implement a code review pipeline that traverses an existing source tree, produces
per-file review findings (written as scratch `.md` files co-located with source),
aggregates them into per-directory review reports, and cleans up intermediate
artifacts after each integrate step. Output: one `{dirname}-review.md` per
directory level; source tree is clean when complete.

## Context

Brainstorm: `sandbox/brainstorm-pipeline-repurposing.md`

Uses the same orchestrator infrastructure as the build pipeline. New elements:

- `review.json` machine file
- Role prompts: REVIEW_ARCHITECT (decompose + atomic), REVIEW_IMPLEMENTOR, REVIEW_INTEGRATOR
- POST_IMPLEMENT_HANDLER configured with `golangci-lint ./...` and `go vet ./...`
- POST_INTEGRATE_HANDLER (new internal handler): deletes consumed scratch files
  (`*-review.md` for individual files) after the integrate agent aggregates them
- `"type": "file"` component support (see 49352f-0003/0004)
- Level-scoped handoff history (see 49352f-0005) so REVIEW_INTEGRATOR sees all
  sibling findings for cross-component analysis

**Role mapping:**

| Role | Job |
|------|-----|
| REVIEW_ARCHITECT (decompose) | Identify review scope — sub-components and individual files to review. Return components JSON. |
| REVIEW_IMPLEMENTOR | Review each file; write `{filename}-review.md` scratch artifact |
| POST_IMPLEMENT_HANDLER | Run `golangci-lint`, `go vet` — deterministic static analysis |
| REVIEW_INTEGRATOR | Aggregate per-file reviews + static analysis into `{dirname}-review.md`; identify cross-component issues |
| POST_INTEGRATE_HANDLER | Delete consumed per-file scratch `.md` files |

**Scratch pad pattern:** intermediate per-file review files are co-located with
source for easy navigation during the run; deleted by POST_INTEGRATE_HANDLER after
aggregation. Final output: one review doc per level.

**Depends on:** 49352f subtasks 0003, 0004, 0005; POST_INTEGRATE_HANDLER is a new
internal handler not yet defined in any 49352f subtask.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
