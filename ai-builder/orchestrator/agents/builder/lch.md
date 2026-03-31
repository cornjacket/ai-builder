# agents/lch.py

`LCHAgent` (Leaf Complete Handler) — runs `on-task-complete.sh` and maps its
output tokens to pipeline outcomes.

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
| `NEXT <path>` | `HANDLER_SUBTASKS_READY` — advance to next sibling |
| `DONE` | `HANDLER_ALL_DONE` — pipeline complete |
| `STOP_AFTER` | `HANDLER_STOP_AFTER` — paused by `stop-after` flag |
| `TOP_RENAME_PENDING <dir>` | captured and appended to response for orchestrator to apply after metrics flush |

**Returns `AgentResult` with** one of the three outcomes above, or `exit_code=1`
if `on-task-complete.sh` fails or emits no recognised token.

## TOP_RENAME_PENDING protocol

When the top-level build directory rename is deferred (so the orchestrator can
flush final metrics while paths are still valid), `advance-pipeline.sh` emits
`TOP_RENAME_PENDING <dir>`. LCHAgent captures this in the response string; the
orchestrator applies the rename after `write_metrics_to_task_json(final=True)`.

## Context dependency

Requires `AgentContext` (`ctx.current_job_file`, `ctx.pm_scripts_dir`,
`ctx.run_dir`, `ctx.epic`). Constructed with `LCHAgent(ctx=ctx)`.
