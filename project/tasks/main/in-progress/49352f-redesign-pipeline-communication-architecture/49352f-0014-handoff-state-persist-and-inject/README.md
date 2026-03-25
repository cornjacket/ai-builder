# Task: handoff-state-persist-and-inject

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status      | —                      |
| Epic        | main               |
| Tags        | —               |
| Parent      | 49352f-redesign-pipeline-communication-architecture             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Persist handoff state to `handoff-state.json` in the output directory after
every pipeline stop point, and add a `--handoff-file` flag to inject that state
at startup. Auto-load `handoff-state.json` when `--resume` is passed.

## Context

`handoff_history` and `frame_stack` currently live only in memory. Any
`--resume` or `--start-state` invocation starts with an empty list, so resumed
agents have impoverished context — they don't know what prior agents said or did.
This also blocks the component-test mechanism (subtask 0015), which needs to
inject handoff state from a prior step's gold output.

**Changes required:**

1. **Persist on stop.** After every stop point (clean completion, `stop-after`,
   `NEED_HELP`, or interrupt) the orchestrator writes `handoff-state.json` to
   the output directory:
   ```json
   {
     "handoff_history": ["[ARCHITECT] ...", "[DECOMPOSE_HANDLER] ..."],
     "frame_stack": [{"anchor_index": 1, "scope_dir": "/path/to/build-1"}]
   }
   ```

2. **`--handoff-file <path>` flag.** On startup, optionally load a JSON file to
   pre-populate `handoff_history` and `frame_stack` before the first agent runs.
   Prompt building proceeds normally — the full code path is exercised.

3. **`--resume` auto-load.** When `--resume` is passed and `handoff-state.json`
   exists in the output directory, load it automatically. No separate
   `--handoff-file` needed for the normal resume case.

**Key constraint:** `--handoff-file` must populate the internal data structures
(`handoff_history`, `frame_stack`), not inject a pre-built prompt. Prompt
building must run from those structures so the full orchestrator code path is
exercised on every test.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
