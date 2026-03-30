# Task: add-readme-validation-to-regression-gold-tests

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 69f226-pipeline-doc-generation-bugs             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Add README.md presence/absence validation to each regression gold test. Tests should
confirm a README.md exists at every architecturally/functionally relevant directory
level and confirm its absence at language-convention directories (e.g. Go's `internal/`).
All violations must be accumulated and reported together — no fail-fast.

## Context

Currently the gold tests validate file content but not README.md coverage at
intermediate directory levels. After 0002 lands (ARCHITECT generates composite
READMEs), regression runs will produce READMEs at composite source levels. The gold
tests need to assert this.

**Rules for Go projects:**
- `internal/` — language visibility boundary, no README expected; assert its absence
- `internal/<package>/` — architecturally relevant; README required
- `internal/<package>/<component>/` — architecturally relevant; README required

**Implementation:**
- Add a `checkReadmeCoverage(t, outputDir)` helper to each gold test package
- Walk the output directory tree; for each directory apply the rules above
- Accumulate all failures; report them all via `t.Errorf` (not `t.Fatalf`)
- Update gold state fixtures to include the expected README files (will fail until
  0002 is implemented and a fresh regression is run)

The gold tests are expected to **fail** after this subtask until 0002 is complete
and the regression is re-run to generate the missing READMEs.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
