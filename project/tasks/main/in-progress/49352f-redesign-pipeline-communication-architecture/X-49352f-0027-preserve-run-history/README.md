# Task: preserve-run-history

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 49352f-redesign-pipeline-communication-architecture             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Update `reset.sh` (all regressions) to archive each pipeline run into a
timestamped `runs/YYYY-MM-DD-HH-MM-SS/` directory before wiping, so that
every run is preserved for historical comparison. Keep `last_run/` as a
symlink to the most recent entry for backward compatibility.

## Context

`reset.sh` currently saves only to `last_run/` — a single slot that is
overwritten on every reset. It also no longer saves useful structured data:
the old `run-metrics.json` and `run-summary.md` were removed in subtask 0017
and never replaced. `task.json` (which now contains `execution_log` and
`run_summary`) is not saved at all.

**What each run archive should contain:**

| File | Source | Notes |
|------|--------|-------|
| `task.json` | Level:TOP `task.json` from target repo | Contains `execution_log`, `run_summary`, token totals |
| `execution.log` | `output_dir/execution.log` | Raw agent output log |
| `README.md` | Level:TOP pipeline README from target repo | Rendered execution log table |

**Directory layout:**
```
tests/regression/platform-monolith/
  runs/
    2026-03-27-23-45-00/   ← first run
      task.json
      execution.log
      README.md
    2026-03-27-01-12-00/   ← second run
      ...
  last_run -> runs/2026-03-27-01-12-00   ← symlink to most recent
```

**Applies to:** all regression `reset.sh` scripts
(`platform-monolith`, `user-service`, `fibonacci`). Update the shared
`_save_last_run()` pattern in each, or extract a shared helper if the
scripts are refactored.

**Note:** The `runs/` directory should be committed to the repo so run
history is preserved across machines. Add a `.gitkeep` to `runs/` and
ensure `execution.log` and large artifacts are not excluded by `.gitignore`.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

**Reference implementation:** `tests/regression/fibonacci/` already does this
correctly. It has a `results/gemini-run-history.md` with a hand-maintained run
history table (date, elapsed, per-role token counts, gold pass/fail, notes).
Use it as the model for what to produce here. The fibonacci approach is manual
(human fills in the table after each run); this task may automate that step by
having `reset.sh` append a row from the archived `task.json`'s `run_summary`.
