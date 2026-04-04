# Task: always-on-recording

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | draft             |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Category    | orchestrator-core      |
| Created     | 2026-04-03            |
| Completed   | —                      |
| Next-subtask-id | 0004 |

## Goal

Make every pipeline run always-on-recording by default, without requiring
`--record-to`. This decouples debugging capability from whether you thought
to enable recording in advance. Regression tests continue to use the explicit
`--record-to` / push flow; always-on recording just means non-regression runs
also capture AI responses and workspace snapshots.

Key design decisions to resolve:

1. **Default recording location** — `sandbox/recordings/<run-timestamp>/` or
   alongside the output dir. Must NOT be inside `output/` or `target/` — the
   recording dir captures those directories and nesting would cause
   compare_snapshot to always produce spurious diffs.

2. **Retention policy** — three modes, configurable per run or via a settings
   file:
   - **ephemeral** — recording is created, run completes, then automatically
     wiped. Inspect it before it's gone if needed; no persistent disk cost.
     Suitable as the default for non-regression runs.
   - **local-rolling** — keep only the most recent N recordings for this
     pipeline (keyed by output dir path or pipeline name). Older ones deleted
     on next run.
   - **regression** — explicit `--record-to` with push to `ai-builder-recordings`.
     Already implemented. Local copy is the golden recording.

3. **Settings file** — where should the retention policy live? Candidates:
   a) A CLI flag (`--record-retention ephemeral|rolling|regression`)
   b) A per-test config file alongside `record.sh`
   c) A repo-level settings file (`ai-builder/orchestrator/settings.json`)

4. **Disk budget** — a full recording (output/ + target/ snapshots, N
   invocations) can be 50–100 MB. With ephemeral mode, cost is near-zero.
   With rolling mode, cap should be configurable (default: last 3 runs).

## Context

Currently the orchestrator only writes AI responses to files and takes git
snapshots when `--record-to` is explicitly passed. In non-record mode, the
full AI response text is parsed for OUTCOME/HANDOFF and discarded — there is
no post-hoc way to inspect what the AI produced for a failed run.

The recording infrastructure is cheap (write text files + `git commit`) relative
to AI call latency. Making it always-on costs nothing at runtime and provides
significant debugging value: if a live run fails, you can inspect exactly what
each AI invocation produced without having to reproduce the failure.

The recording dir must sit alongside `output/` and `target/`, not inside either.
If placed inside `output/`, `compare_snapshot.py`'s `git diff -- output/` would
include the recording's own files as spurious diffs.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [ ] [afed3c-0000-design-retention-policy](afed3c-0000-design-retention-policy/)
- [ ] [afed3c-0001-implement-always-on-recording](afed3c-0001-implement-always-on-recording/)
- [ ] [afed3c-0002-implement-retention-cleanup](afed3c-0002-implement-retention-cleanup/)
- [ ] [afed3c-0003-document-always-on-recording](afed3c-0003-document-always-on-recording/)
<!-- subtask-list-end -->

## Notes

_None._
