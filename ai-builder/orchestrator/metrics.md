# metrics.py

Captures per-invocation timing and token usage during a pipeline run. Writes
a live execution log to the Level:TOP task README after each invocation, and
produces `run-summary.md` and `run-metrics.json` on pipeline completion.

The orchestrator owns all monitoring. Agents are entirely unaware of this
module. These functions are the seam for future persistence (database, API):
replace or wrap them without touching `orchestrator.py`.

---

## Data Model

### `InvocationRecord`

```python
@dataclass
class InvocationRecord:
    role: str           # Role name, e.g. "ARCHITECT"
    agent: str          # CLI agent name, e.g. "claude", "gemini"
    n: int              # Per-role invocation count (1-based)
    description: str    # Human-readable task name derived from job doc path
    start: datetime
    end: datetime
    elapsed: timedelta  # end - start
    tokens_in: int
    tokens_out: int
    tokens_cached: int
    outcome: str        # e.g. "ARCHITECT_DECOMPOSITION_READY"
```

### `RunData`

```python
@dataclass
class RunData:
    task_name: str                      # Derived from initial job doc path
    start: datetime                     # Set at orchestrator startup
    invocations: list[InvocationRecord] # Appended by record_invocation()
    end: datetime | None                # Set by orchestrator on completion
```

---

## Public API

### `record_invocation(run, role, agent, role_counter, description, start, end, tokens_in, tokens_out, tokens_cached, outcome) -> InvocationRecord`

Creates an `InvocationRecord` and appends it to `run.invocations`. Computes
`elapsed = end - start`.

| Parameter | Type | Description |
|-----------|------|-------------|
| `run` | `RunData` | Accumulator for the current pipeline run |
| `role` | str | Role name |
| `agent` | str | Agent CLI name |
| `role_counter` | int | How many times this role has been invoked in this run |
| `description` | str | Human-readable task name (see `description_from_job_path`) |
| `start` | datetime | Invocation start (captured before `run_agent` call) |
| `end` | datetime | Invocation end (captured after `run_agent` returns) |
| `tokens_in` | int | Input tokens from `AgentResult.tokens_in` |
| `tokens_out` | int | Output tokens from `AgentResult.tokens_out` |
| `tokens_cached` | int | Cache-read input tokens from `AgentResult.tokens_cached` |
| `outcome` | str | Parsed outcome string |

---

### `description_from_job_path(job_path) -> str`

Derives a human-readable description from a job document path by stripping
the leading task ID prefix from the directory name.

| Directory name | Output |
|----------------|--------|
| `51de6e-0001-handler/README.md` | `handler` |
| `fa3480-build-1/README.md` | `build-1` |
| `eab6f7-user-service/README.md` | `user-service` |
| `None` | `—` |

Pattern rules (applied in order):
1. Strip `{6-hex}-{4-digit}-` prefix (incremental subtask format)
2. Strip `{6-hex}-` prefix (top-level task format)
3. Return the directory name unchanged if neither matches

---

### `update_task_doc(build_readme, run) -> None`

Rewrites the `## Execution Log` table in the Level:TOP pipeline-subtask README
after each agent invocation. Called by the orchestrator immediately after
`record_invocation`.

**If `## Execution Log` is absent:** inserts it after the `## Goal` section
(before the next `##` heading) with the column headers. This means the section
does not need to be present in the template — it is created dynamically on the
first invocation.

**If `## Execution Log` is present:** replaces only the `## Execution Log`
section, stopping at the next `## ` heading. Sections that follow (Design,
Acceptance Criteria, Subtasks, etc.) are preserved.

Columns: `# | Role | Agent | Description | Ended | Elapsed | Tokens In | Tokens Out | Tokens Cached`

Does nothing if `build_readme` does not exist (e.g. after the Level:TOP
directory has been renamed by `on-task-complete.sh`).

---

### `write_run_summary(output_dir, run) -> None`

Writes `run-summary.md` to `output_dir` on pipeline completion. Content is
a `# Run Summary — {task_name}` heading followed by the shared summary body
(see `_build_summary_lines`).

---

### `write_run_metrics_json(output_dir, run) -> None`

Writes `run-metrics.json` to `output_dir` on pipeline completion. Contains
the same data as `run-summary.md` in machine-readable form.

Top-level keys: `task_name`, `start`, `end`, `elapsed_s`, `invocations`.

Each invocation object: `role`, `agent`, `n`, `description`, `start`, `end`,
`elapsed_s`, `tokens_in`, `tokens_out`, `tokens_cached`, `outcome`.

All datetimes are ISO 8601 strings; elapsed values are floats (seconds).

---

### `write_summary_to_readme(build_readme, run) -> None`

Appends a `## Run Summary` section to the Level:TOP README on pipeline
completion. Content is identical to `run-summary.md` body (same
`_build_summary_lines` output). Uses sub-headings (`###`) so the sections
nest correctly under `## Run Summary`.

Does nothing if `build_readme` does not exist.

---

## Private Functions

### `_build_summary_lines(run) -> list[str]`

Shared body builder used by `write_run_summary` and `write_summary_to_readme`.
Returns a list of markdown lines covering:

1. **Header table** — task name, start/end times, total elapsed, invocation
   count, and overall token totals (in, out, cached, combined).
2. **`### Invocations`** — per-invocation table with the same columns as the
   live execution log.
3. **`### Per-Role Totals`** — count and total/average elapsed per role.
4. **`### Token Usage by Role`** — token breakdown per role with a bold
   `Total` footer row.
5. **`### Invocations by Agent`** — how many invocations each agent handled.

---

### `_fmt_elapsed(td) -> str`

Formats a `timedelta` as `Xm YYs` (e.g. `2m 05s`) or `Xs` (e.g. `47s`) for
sub-minute durations.

---

## Outputs

| File | When written | Description |
|------|-------------|-------------|
| Level:TOP `README.md` (partial rewrite) | After each invocation | Live `## Execution Log` table |
| `run-summary.md` | Pipeline completion | Human-readable run summary |
| `run-metrics.json` | Pipeline completion | Machine-readable run data |
| Level:TOP `README.md` (append) | Pipeline completion | `## Run Summary` section |

End-of-run files (`run-summary.md`, `run-metrics.json`, appended README) are
only written when the pipeline completes normally. Timeout, agent error, and
`_NEED_HELP` halts exit before the end-of-run block in `orchestrator.py`.

---

## Token Fields

Token counts are non-zero only for the `claude` agent. The `claude` CLI's
`stream-json` output includes a `result` event with a `usage` object
(`input_tokens`, `output_tokens`, `cache_read_input_tokens`). Other agents
return zeros for all token fields.
