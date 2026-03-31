# agents/decompose.py

`DecomposeAgent` — creates pipeline subtask directories from ARCHITECT's
components list and advances `current-job.txt` to the first component.

## run(job_doc, output_dir, **kwargs)

**Inputs:**
- `job_doc: Path` — path to the parent task's `README.md`
- `output_dir: Path` — unused directly; `parent_output_dir` is read from
  `task.json["output_dir"]` with `ctx.output_dir` as fallback
- `kwargs["components"]` — list of component dicts from ARCHITECT's JSON response;
  each entry has `name`, `complexity`, `description`, and optional `source_dir`

**Reads:**
- `job_doc.parent/task.json` — `level`, `depth`, `output_dir`, `stop-after`

**Writes (per component):**
- Calls `new-pipeline-subtask.sh` to create the subtask directory
- Updates `task.json` in the new subtask with `name`, `complexity`, `depth`,
  `goal`, `context`, `output_dir`; sets `last-task` and `level` on the final
  component
- Updates the subtask `README.md` Goal and Context sections
- Creates a placeholder `README.md` in `comp_output_dir` if `source_dir` is set

**Writes (pipeline pointer):**
- Calls `set-current-job.sh --output-dir ctx.run_dir` pointing at first subtask

**Returns `AgentResult` with:**
- `OUTCOME: HANDLER_SUBTASKS_READY` — components created, pipeline advances
- `OUTCOME: HANDLER_STOP_AFTER` — `stop-after: true` on parent task; pauses here
- `exit_code=1` on any script failure or missing data

## Context dependency

Requires `AgentContext` (`ctx.target_repo`, `ctx.pm_scripts_dir`, `ctx.epic`,
`ctx.output_dir`, `ctx.run_dir`). Constructed with `DecomposeAgent(ctx=ctx)`.
