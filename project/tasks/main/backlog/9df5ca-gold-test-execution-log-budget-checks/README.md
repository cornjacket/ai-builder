# Task: gold-test-execution-log-budget-checks

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Add per-row budget checks to the service regression gold tests. Each row in
the execution log of a completed pipeline task README should be validated
against a per-regression budget file that specifies max and min thresholds
for elapsed time and token counts. Violations are reported as test errors
(max exceeded) or warnings (min not reached). A summary of all violations
is appended to the pipeline task's README after the Run Summary section.

## Context

The execution log in `X-<build>/README.md` records per-invocation elapsed
time and token counts. As the pipeline evolves, regressions in cost or
performance (e.g. a role becoming unexpectedly slow or token-heavy) should
be caught automatically rather than noticed by manual inspection.

Symmetrically, when performance improves the test suite should flag that too
so budget values can be tightened, keeping the budget meaningful over time.

## Behaviour

### Budget file

Each regression test directory contains a `budget.json` (or `budget.yaml`)
that maps role+description keys to threshold objects. Example:

```json
{
  "ARCHITECT/store":     { "max_elapsed_s": 180, "min_elapsed_s": 10, "max_tokens_out": 6000, "min_tokens_out": 500 },
  "IMPLEMENTOR/store":   { "max_elapsed_s": 240, "min_elapsed_s": 15, "max_tokens_out": 8000, "min_tokens_out": 1000 },
  "TESTER/store":        { "max_elapsed_s":  30, "min_elapsed_s":  1 },
  "LEAF_COMPLETE_HANDLER/store": { "max_elapsed_s": 20, "min_elapsed_s": 0 }
}
```

Keys are `"<Role>/<description>"` matching the `role` and `description`
columns of the execution log. Internal roles (DOCUMENTER_*, DECOMPOSE_HANDLER,
LEAF_COMPLETE_HANDLER) may omit token thresholds since they always report 0.

### Violation rules

- **Max violation (error):** `actual > max_<field>` — test fails via
  `t.Errorf`. Indicates a regression in cost or performance.
- **Min violation (warning):** `actual < min_<field>` — logged via
  `t.Logf` with a `BUDGET WARNING` prefix. Indicates an improvement;
  the budget value should be tightened. Does not fail the test.

### README annotation

After the Run Summary section in the pipeline task's README, append a
`## Budget Violations` section (written by the gold test helper, not by
the pipeline itself). It lists each violation — max or min — with the
field name, threshold, and actual value. If there are no violations the
section is omitted.

Example:

```markdown
## Budget Violations

| Row | Field | Threshold | Actual | Severity |
|-----|-------|-----------|--------|----------|
| ARCHITECT/store | elapsed_s | max 180s | 210s | ERROR |
| LEAF_COMPLETE_HANDLER/store | elapsed_s | min 0s | — | OK (no min violation) |
```

### goldutil API

New function in `goldutil`:

```go
func CheckExecutionLogBudget(t *testing.T, targetDir, budgetFile string)
```

- Walks `targetDir` for completed TOP-level pipeline task READMEs
  (same selection logic as `CheckRunSummaryExists`)
- Reads the corresponding `task.json` execution_log
- Loads the budget from `budgetFile`
- Evaluates each row against its budget entry (unmatched rows are skipped)
- Reports max violations as `t.Errorf`, min violations as `t.Logf`
- Appends the `## Budget Violations` section to the pipeline task README

### Gold test wiring

```go
func TestExecutionLogBudget(t *testing.T) {
    goldutil.CheckExecutionLogBudget(t, targetDir,
        filepath.Join("testdata", "budget.json"))
}
```

Each regression (`user-service`, `platform-monolith`) carries its own
`testdata/budget.json` with thresholds derived from observed baseline runs.

## Selecting threshold values

Before the budget files can be written, actual min and max values must be
chosen for each row. This is a required subtask.

**AI agent roles** (ARCHITECT, IMPLEMENTOR) require four thresholds per row:
- `min_elapsed_s` / `max_elapsed_s`
- `min_tokens_out` / `max_tokens_out`

**Internal agent roles** (TESTER, TESTER, LEAF_COMPLETE_HANDLER,
DECOMPOSE_HANDLER, DOCUMENTER_POST_ARCHITECT, DOCUMENTER_POST_IMPLEMENTOR)
always report 0 tokens, so only elapsed time thresholds are needed:
- `min_elapsed_s` / `max_elapsed_s`

### Process for setting values

1. Use the observed baseline run as the midpoint. The user-service regression
   run on 2026-03-30 (`sandbox/user-service-target`, build `86a08c-0000-build-1`)
   provides the initial data set.
2. Apply a tolerance band to each observed value:
   - **max** = observed × 2.0 (allow for model variance and slower hardware)
   - **min** = observed × 0.25 (flag if suspiciously fast — possible skip or
     trivial output)
3. Round to a sensible precision (e.g. elapsed to nearest 5 s, tokens to
   nearest 500).
4. Review the resulting values for sanity before committing the budget files.
   Thresholds that are obviously too tight or too loose should be adjusted by
   hand.

The selected values must be documented in each regression's `testdata/budget.json`
and reviewed alongside the implementation PR.

## Notes

- The `## Budget Violations` section written to the README is advisory —
  it is regenerated on each gold test run and should not be committed.
- Min thresholds exist primarily to detect unexpectedly fast runs that may
  indicate a role is being skipped or producing trivially short output.
- Token thresholds apply only to AI agent roles (ARCHITECT, IMPLEMENTOR);
  internal roles always report 0 tokens and must not have token budget fields.
