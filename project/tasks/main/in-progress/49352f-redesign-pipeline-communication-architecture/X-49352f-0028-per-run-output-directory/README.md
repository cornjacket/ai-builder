# Task: per-run-output-directory

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

Add a `--run-dir` CLI flag to the orchestrator. All per-run sidecar files
(`execution.log`, `handoff-state.json`, `current-job.txt`, `last-job.json`)
are written to `--run-dir` instead of `--output-dir`. This separates the
pipeline's coordination state from the generated code output, allowing
multiple pipelines to run concurrently against different target repos without
their state files colliding.

## Context

Currently all orchestrator sidecar files land in `--output-dir`:
- `execution.log` — raw agent output log
- `handoff-state.json` — handoff/frame stack for resume
- `current-job.txt` — pipeline cursor
- `last-job.json` — pointer to active task for resume

Because these are all in the same directory, two concurrent pipelines writing
to different subdirectories of the same `--output-dir` (or different output
dirs on the same machine) still conflict if `--output-dir` is shared. Worse,
`execution.log` and `current-job.txt` are flat files — two pipelines would
interleave their writes.

**Fix:** introduce `--run-dir` (defaults to `--output-dir` for backward
compatibility). The orchestrator writes all coordination/sidecar files to
`--run-dir`. Generated source code still goes to `--output-dir`. Each
concurrent pipeline gets its own `--run-dir` (e.g. `runs/2026-03-27-A/`,
`runs/2026-03-27-B/`).

**Files to move to `--run-dir`:**
| File | Current location | New location |
|------|-----------------|--------------|
| `execution.log` | `output_dir/` | `run_dir/` |
| `handoff-state.json` | `output_dir/` | `run_dir/` |
| `current-job.txt` | `output_dir/` | `run_dir/` |
| `last-job.json` | `output_dir/` | `run_dir/` |

**`--run-dir` also serves as the natural archive location** for subtask 0028
(preserve-run-history): `reset.sh` copies the run dir to `runs/` before
wiping, giving a complete per-run snapshot without needing to hunt across
multiple locations.

**Backward compatibility:** default `--run-dir` to `--output-dir` so existing
invocations and regression scripts require no changes unless they opt in to
parallel runs.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
