# Task: reset-run-and-gold-scripts

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

Write `run.sh`, `doc-spec.md`, and `gold/gold_test.go` for the
doc-platform-monolith regression test. Run the full pipeline and confirm all
gold checks pass.

## Context

**`run.sh`** — mirror `doc-user-service/run.sh`: reads `--job` from
`current-job.txt`, runs orchestrator with `machines/doc/default.json` and
`sandbox/doc-platform-monolith-output/` as `--output-dir`.

**`doc-spec.md`** — Goal: generate documentation for the platform-monolith
source tree. Context: pipeline must traverse recursively, write companion `.md`
and `README.md` per directory, never modify source files. The source already
has `internal/iam/README.md` and `internal/metrics/README.md` — the pipeline
should add to these directories, not fail because docs already exist.

**`gold/gold_test.go`** — verify ALL expected `.md` files are present after the
run. Must check both pre-existing docs (which should still be there) and all
newly generated docs. Expected files include at minimum:

- Root `README.md`
- `cmd/README.md` and `cmd/platform/README.md`, `cmd/platform/main.go.md`
- `internal/README.md`, `internal/iam/README.md` (pre-existing — must still exist)
- `internal/iam/iam.go.md`, `internal/iam/lifecycle/README.md`, `internal/iam/lifecycle/lifecycle.go.md`
- `internal/iam/authz/README.md`, `internal/iam/authz/authz.go.md`
- `internal/metrics/README.md` (pre-existing — must still exist)
- `internal/metrics/metrics.go.md`, `internal/metrics/handlers/README.md`
- `internal/metrics/handlers/handlers.go.md`, `internal/metrics/store/README.md`
- `internal/metrics/store/store.go.md`

Also check that source `.go` files are unmodified (spot-check at least one).

**`gold/go.mod`** — module: `github.com/cornjacket/ai-builder/tests/regression/doc-platform-monolith/gold`

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
