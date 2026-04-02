# agents/lch.py

`LCHAgent` (Leaf Complete Handler) — runs `on-task-complete.sh` and maps its
output tokens to pipeline outcomes. Supports declarative outcome routing via
an optional `route_on` config.

## run(job_doc, output_dir, **kwargs)

**Inputs:**
- `job_doc: Path` — unused (LCH operates on the current task recorded in
  `ctx.current_job_file`, not on `job_doc` directly)
- `output_dir: Path` — unused

**Reads:** `ctx.current_job_file` — path to `current-job.txt`; contains the
active task README path passed to `on-task-complete.sh`

**Executes:**
```
on-task-complete.sh --current <job_path> --output-dir <ctx.run_dir> --epic <ctx.epic>
```

**Parses stdout tokens:**
| Token | Outcome |
|-------|---------|
| `NEXT <path>` | `HANDLER_SUBTASKS_READY` (default) or a mapped outcome from `route_on` |
| `DONE` | `HANDLER_ALL_DONE` — pipeline complete |
| `STOP_AFTER` | `HANDLER_STOP_AFTER` — paused by `stop-after` flag |
| `TOP_RENAME_PENDING <dir>` | captured and appended to response for orchestrator to apply after metrics flush |

**Returns `AgentResult` with** one of the outcomes above, or `exit_code=1`
if `on-task-complete.sh` fails or emits no recognised token.

## route_on config

The `route_on` config (passed from the machine JSON via the orchestrator)
allows LCH to emit different outcomes for `NEXT` tokens based on a field in
the next task's `task.json`. This lets a single machine JSON route different
subtask types to different agents without any orchestrator core changes.

**Config schema:**
```json
"route_on": {
    "field":     "<task.json field name>",
    "default":   "<outcome when field is absent or unrecognised>",
    "<value>":   "<outcome when field equals this value>"
}
```

`field` and `default` are required. Additional keys are the possible field
values mapped to their outcome tokens.

**Example — doc pipeline routes `integrate` subtasks directly to DOC_INTEGRATOR:**
```json
"route_on": {
    "field":     "component_type",
    "default":   "HANDLER_SUBTASKS_READY",
    "integrate": "HANDLER_INTEGRATE_READY"
}
```

When `on-task-complete.sh` emits `NEXT <path>`, LCH reads `task.json` in the
same directory as `<path>`, checks the `component_type` field, and returns
`HANDLER_INTEGRATE_READY` if `component_type == "integrate"`, otherwise
`HANDLER_SUBTASKS_READY`.

If `route_on` is absent, LCH always emits `HANDLER_SUBTASKS_READY` for `NEXT`
tokens (original behaviour, preserved for the builder pipeline).

## TOP_RENAME_PENDING protocol

When the top-level build directory rename is deferred (so the orchestrator can
flush final metrics while paths are still valid), `advance-pipeline.sh` emits
`TOP_RENAME_PENDING <dir>`. LCHAgent captures this in the response string; the
orchestrator applies the rename after `write_metrics_to_task_json(final=True)`.

## Context dependency

Requires `AgentContext` (`ctx.current_job_file`, `ctx.pm_scripts_dir`,
`ctx.run_dir`, `ctx.epic`). Constructed with `LCHAgent(ctx=ctx, route_on=...)`.
