# Task: doc-platform-monolith-regression-test

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | b9529c-doc-pipeline             |
| Priority    | —           |
| Next-subtask-id | 0005 |

## Goal

Add a `doc-platform-monolith` regression test that runs the doc pipeline against
the platform-monolith source tree and verifies all expected `.md` files are produced.

## Context

The platform-monolith source tree is more complex than user-service — it has
multiple top-level service packages (`cmd/platform/`, `internal/metrics/`,
`internal/iam/`) each with subdirectories (`handlers/`, `store/`, `lifecycle/`,
`authz/`). This exercises the doc pipeline's composite-node DOC_INTEGRATOR path
more deeply than the user-service test.

**Key difference from doc-user-service:** The source template retains some
pre-existing lower-level `.md` files — specifically `internal/iam/README.md`
and `internal/metrics/README.md`. These simulate a realistic "partial
documentation" scenario where some sub-component docs already exist. The
pipeline should produce new docs where none exist and co-exist with the
pre-existing ones. The gold test must confirm ALL expected `.md` files are
present after the run — both the pre-existing ones and all newly generated ones.

Source: Go files from `sandbox/platform-monolith-output/` (all `.go` files
across `cmd/`, `internal/`). Retain `internal/iam/README.md` and
`internal/metrics/README.md` in the template; strip all other `.md` files
(including `master-index.md`).

Output will go to `sandbox/doc-platform-monolith-output/`.
Target task tree will live in `sandbox/doc-platform-monolith-target/`.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [x] [X-b9529c-0000-create-regression-test-dir](X-b9529c-0000-create-regression-test-dir/)
- [x] [X-b9529c-0001-copy-platform-monolith-source-as-template](X-b9529c-0001-copy-platform-monolith-source-as-template/)
- [x] [X-b9529c-0002-reset-copies-source-to-sandbox](X-b9529c-0002-reset-copies-source-to-sandbox/)
- [x] [X-b9529c-0003-setup-task-system-and-pipeline-task](X-b9529c-0003-setup-task-system-and-pipeline-task/)
- [x] [X-b9529c-0004-reset-run-and-gold-scripts](X-b9529c-0004-reset-run-and-gold-scripts/)
<!-- subtask-list-end -->

## Notes

The gold test (sub-subtask 0004) must include a `TestMasterIndexExists` check.
`master-index.md` is written to the root of `--output-dir` at orchestrator
teardown — it is not part of the source template and must be present after the
run.
