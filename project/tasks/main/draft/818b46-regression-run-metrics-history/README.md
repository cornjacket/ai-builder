# Task: regression-run-metrics-history

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | draft             |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Category    | regression-infra       |
| Next-subtask-id | 0000               |

## Goal

Record `run-metrics.json` to a persistent results history under each regression
test directory after every successful run, and surface these results as part of
the gold test suite so performance regressions are visible alongside behavioral
regressions.

## Context

### Why

Every pipeline run produces a `run-metrics.json` with total elapsed time,
per-role token counts (input, output, cached), and invocation counts. Currently
this data is:
- Ephemeral — overwritten on the next run
- Partially preserved — `reset.sh` saves only the _last_ run to `last_run/`
- Invisible to gold tests — gold tests verify behavioral contracts but say
  nothing about performance

As optimizations accumulate (internal handlers, scope-bounded history, prompt
caching, stale output wipe) we need a growing record showing how each run
compares to all prior runs, not just the immediately preceding one.

### Existing infrastructure

- `run-metrics.json` written by `metrics.py` on normal pipeline completion.
  Schema: `{ task_name, start, end, elapsed_s, invocations: [ { role, agent, n,
  description, start, end, elapsed_s, tokens_in, tokens_out, tokens_cached,
  outcome } ] }`.
- `reset.sh` already saves the last run to `tests/regression/<name>/last_run/`.
- Gold tests use `TestMain` to build/start the generated binary, run all tests,
  then exit. Currently assert behavioral contracts only.
- `goldutil` provides shared helpers (`FindMainPackage`, `BuildBinary`,
  `WaitReady`, `MustDo`, `ExtractField`).

### Tests that produce run-metrics.json

| Test | Pipeline type | Notes |
|------|--------------|-------|
| `fibonacci` | non-TM (simple.json) | Single ARCHITECT→IMPLEMENTOR→TESTER |
| `user-service` | TM (default.json) | Single-level decomposition |
| `platform-monolith` | TM (default.json) | Multi-level, tree traversal |
| `template-setup` | bash only | No pipeline; no run-metrics.json |

### Design

**Results storage:** `tests/regression/<name>/results/` — one JSON file per run
named by start timestamp (`YYYY-MM-DDTHH-MM-SS.json`). Gitignored (local history
only). Schema mirrors `run-metrics.json`, with `gold_pass bool` appended.

**Results storage:** `tests/regression/<name>/results/` — one JSON file per run
named by start timestamp (`YYYY-MM-DDTHH-MM-SS.json`). Gitignored (local history
only).

**Recording trigger:** Hook into gold `TestMain` — capture `exitCode :=
m.Run()`, always record (even on failure), then call `os.Exit(exitCode)`.
Single command tests and records.

**Eligibility tagging:** Not all runs are valid performance baselines. Each
result JSON includes:

```json
{
  ...run-metrics fields...,
  "gold_pass": true,
  "is_resumed": false,
  "eligible_for_comparison": true
}
```

- `is_resumed` — detected by counting `=== Orchestrator: starting ===` lines
  in `execution.log`. More than one means the pipeline stalled mid-run (quota
  exhaustion, hours-long cap) and the user manually resumed with `--resume` or
  `--clean-resume`. The `run-metrics.json` only covers the resumed portion, so
  token and elapsed totals are incomplete and not comparable.
- `eligible_for_comparison = gold_pass && !is_resumed`

**Note on transient rate limiting:** Short-term token-bucket throttling
(`rate_limit_event` in the execution log) is normal — the claude CLI retries
automatically within seconds and the pipeline continues without intervention.
These runs are valid and eligible. Only quota exhaustion that forces a manual
resume disqualifies a run.

**Best/worst tracking:** After each eligible run, `RecordRunMetrics` updates
two named reference files in `results/`:
- `best.json` — lowest total output tokens among eligible runs (proxy for
  "model did the right thing on a clean slate")
- `worst.json` — highest total output tokens among eligible runs (upper bound)

Elapsed time is recorded separately as `best_elapsed.json` / `worst_elapsed.json`
since a fast run with high output tokens (stale code rewrite) is a different
failure mode from a slow run with normal output tokens (rate limits already
excluded).

**Pass/fail signal (deterministic):** The gold test emits a warning (not a
failure) if the current eligible run's invocation count per role deviates from
the previous eligible run. Internal handlers (DECOMPOSE_HANDLER, LCH) must
each complete in <10s or the warning is escalated to a test failure.

**Summary output:** After recording, print a human-readable comparison vs. the
previous eligible entry — elapsed delta, output token delta, cached token delta,
per-role breakdown. Printed to stdout regardless of eligibility (with a
`[EXCLUDED from comparison: reason]` prefix if ineligible).

**goldutil addition:** Add `RecordRunMetrics(resultsDir, outputDir string,
goldPass bool)` to `goldutil.go`. Called from each gold test's TestMain.

**fibonacci:** Non-TM, 3 invocations — still worth recording for consistency.

### Non-goals

- No failure thresholds on token counts (record and surface, don't fail).
- No cross-machine timing normalisation.
- No aggregation across tests — each keeps its own results history.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
