# Pipeline Monitoring

Design document for the pipeline metrics and observability system in ai-builder.

---

## Design Principles

**The orchestrator owns all monitoring.** Agents run CLI subprocesses and
return text; they have no instrumentation and no awareness of metrics. All
timing, token counting, and reporting is done in `orchestrator.py` and
`metrics.py` after each `run_agent()` call returns.

**Data flows out, not in.** Metrics are written to files (README, output
directory). Nothing in the pipeline reads metrics back. This means monitoring
has no effect on pipeline behavior — it can be stripped out or replaced without
changing any agent output.

**Clean function boundary.** All metrics logic lives in `metrics.py`.
`orchestrator.py` calls five functions: `record_invocation`, `update_task_doc`,
`write_run_summary`, `write_run_metrics_json`, and `write_summary_to_readme`.
To add a new output format (database, HTTP POST, dashboard), add a function to
`metrics.py` and call it from the same points in the orchestrator. No other
changes needed.

---

## What Is Captured

After each agent invocation, the orchestrator records:

| Field | Source |
|-------|--------|
| Role | `current_role` variable |
| Agent | `AGENTS[current_role]` from the machine file |
| Per-role invocation count | `role_counters[role]` (1-based) |
| Description | `description_from_job_path(job_doc)` — see below |
| Start time | Captured immediately before `run_agent()` call |
| End time | Captured immediately after `run_agent()` returns |
| Elapsed | `end - start` (computed in `record_invocation`) |
| Tokens in | `AgentResult.tokens_in` (claude only; 0 for others) |
| Tokens out | `AgentResult.tokens_out` (claude only; 0 for others) |
| Tokens cached | `AgentResult.tokens_cached` (claude only; 0 for others) |
| Outcome | Parsed from agent response |

**Description derivation.** The description is the human-readable portion of
the job document's directory name, with the task ID prefix stripped:
- `51de6e-0003-handler` → `handler`
- `fa3480-build-1` → `build-1`
- `eab6f7-user-service` → `user-service`

This provides readable context in tables without exposing internal IDs.

---

## Live Execution Log

The `## Execution Log` section of the Level:TOP pipeline-subtask README is
rewritten after every agent invocation. This means you can watch the pipeline
progress by reading the task README in real time.

**How it works:**
1. `_find_level_top(job_doc)` checks whether the current job doc is or was the
   Level:TOP README. The result is cached in `build_readme`.
2. After each invocation, `metrics_mod.update_task_doc(build_readme, run)` is
   called if `build_readme` is not `None`.
3. `update_task_doc` rewrites the `## Execution Log` table with all invocations
   so far, then writes the file.

**Section insertion.** The template for Level:TOP pipeline-subtasks no longer
pre-populates `## Execution Log`. On the first invocation, `update_task_doc`
detects that the section is absent and inserts it after the `## Goal` section.
Subsequent calls replace the section in place.

**Column meanings:**

| Column | Meaning |
|--------|---------|
| `#` | Sequential invocation number across all roles |
| Role | Role that ran |
| Agent | CLI agent used |
| Description | Derived from job doc path (see above) |
| Ended | Wall-clock time when invocation finished (`HH:MM:SS`) |
| Elapsed | Duration of the invocation (`Xm YYs` or `Xs`) |
| Tokens In | Input tokens consumed |
| Tokens Out | Output tokens generated |
| Tokens Cached | Cache-read input tokens (reduces effective cost) |

**After the run completes,** the `## Run Summary` section is appended to the
same README. The execution log and the run summary together give a complete
picture of what happened and how long it took.

**Stale path edge case.** `on-task-complete.sh` renames completed task
directories to `X-{name}`. If the Level:TOP directory is renamed during the
final `LEAF_COMPLETE_HANDLER` invocation, `build_readme` points to a path
that no longer exists. `update_task_doc` silently skips non-existent files,
so the last row may not appear in the live log. It still appears in
`run-summary.md`. This is accepted behavior.

---

## End-of-Run Outputs

On normal pipeline completion (after the main loop exits), the orchestrator
writes three outputs:

### `run-summary.md`

Human-readable markdown written to `OUTPUT_DIR/run-summary.md`. Contains:

- **Header table** — task name, start/end timestamps, total elapsed time,
  total invocation count, and aggregate token totals (in, out, cached, combined).
- **Invocations table** — one row per invocation, same columns as the live
  execution log.
- **Per-Role Totals** — invocation count, total time, and average time per
  invocation for each role.
- **Token Usage by Role** — tokens in/out/cached/total per role, with a
  bold grand total footer row.
- **Invocations by Agent** — how many invocations each agent CLI handled.
  Useful when a run mixes `claude` and `gemini` agents.

### `run-metrics.json`

Machine-readable JSON written to `OUTPUT_DIR/run-metrics.json`. Same data as
`run-summary.md`. Top-level structure:

```json
{
  "task_name": "build-1",
  "start": "<ISO 8601>",
  "end": "<ISO 8601>",
  "elapsed_s": 847.3,
  "invocations": [
    {
      "role": "ARCHITECT",
      "agent": "claude",
      "n": 1,
      "description": "build-1",
      "start": "<ISO 8601>",
      "end": "<ISO 8601>",
      "elapsed_s": 62.1,
      "tokens_in": 12450,
      "tokens_out": 3210,
      "tokens_cached": 0,
      "outcome": "ARCHITECT_DECOMPOSITION_READY"
    }
  ]
}
```

### `## Run Summary` in the Level:TOP README

The same summary body (identical content to `run-summary.md`) is appended to
the Level:TOP pipeline-subtask README as a `## Run Summary` section. Sub-headings
use `###` so they nest correctly under `## Run Summary`. This puts the full run
record alongside the task definition in a single document.

**These outputs are only written on normal completion.** Timeout, agent error,
and `_NEED_HELP` halts exit before the end-of-run block. `run-summary.md` and
`run-metrics.json` will not exist for incomplete runs.

---

## Extension Points

To add a new output (database row, HTTP POST, dashboard push):

1. Add a function to `metrics.py` that accepts `(run: RunData)` or
   `(run: RunData, inv: InvocationRecord)`.
2. Call it from `orchestrator.py` at the appropriate point:
   - After each invocation: alongside `metrics_mod.update_task_doc`
   - End of run: alongside `metrics_mod.write_run_summary`

The `InvocationRecord` and `RunData` dataclasses are the stable data contract.
The `_build_summary_lines` helper is private; if you need identical summary
formatting in a new output, import and call it directly.

To change what is captured (e.g., add memory usage), extend `InvocationRecord`,
update `record_invocation`, and update `_build_summary_lines` and
`write_run_metrics_json` to include the new field.

---

## Gemini and Other Agents

Token counts (`tokens_in`, `tokens_out`, `tokens_cached`) are only populated
for the `claude` agent. The claude CLI's `stream-json` format includes a
`result` event with a `usage` object; `agent_wrapper.py` extracts these values.
Other agents return zeros for all token fields.

All other metrics (timing, description, outcome, invocation count) work
identically regardless of agent. Per-role and per-agent tables in the summary
correctly show `0` tokens for non-claude agents, which is accurate — the cost
is not tracked, not missing.
