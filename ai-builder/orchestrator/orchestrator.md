# orchestrator.py

Main pipeline loop for the ai-builder. Reads a job document, drives agents
through a sequence of roles, and halts when the pipeline completes or
encounters an unrecoverable state.

---

## CLI Flags

| Flag | Required | Description |
|------|----------|-------------|
| `--output-dir` | always | Directory for all generated artifacts and logs |
| `--job` | non-TM mode | Path to the job document |
| `--target-repo` | TM mode | Path to target repository; enables TM mode |
| `--epic` | TM mode | Epic name in the task system (default: `main`) |
| `--state-machine` | optional | Path to a JSON machine file; defaults to `machines/builder/default.json` (TM mode) or `machines/builder/simple.json` (non-TM mode) |
| `--start-state` | optional | Override the machine's `start_state` at runtime; must be a role defined in the loaded machine |
| `--resume` | optional | Skip the Level:TOP validation check; use when restarting a mid-run pipeline (see §Resuming a Stalled Run) |
| `--clean-resume` | optional | Like `--resume`, but also deletes the interrupted component's output files before restarting (see §Resuming a Stalled Run). Implies `--resume`. |

`TM_MODE` is true when `--target-repo` is provided. The two modes are
mutually exclusive: `--job` is required in non-TM mode and ignored in TM mode.

`--state-machine` and `--start-state` are orthogonal to the two modes and can
be combined freely. `--start-state` is useful for testing a specific role in
isolation.

---

## Resuming a Stalled Run

If the pipeline halts mid-run (rate limit, agent error, process kill), the
task tree and output dir remain intact. Re-run the orchestrator with the same
arguments plus `--resume`:

```bash
python3 ai-builder/orchestrator/orchestrator.py \
    --target-repo <target> \
    --output-dir  <output> \
    --epic        main \
    --resume
```

`--resume` skips the TM mode validation that requires `current-job.txt` to
point at a Level:TOP pipeline-subtask. On a fresh run this is always true;
on a resume, `current-job.txt` points at whatever internal node was active
when the pipeline stalled, which is correctly INTERNAL level.

### State on resume

The orchestrator is stateless between invocations. Each run creates a fresh
`RunData` with an empty invocations list. The resumed run does not inherit
the stalled run's metrics.

| Artifact | Behaviour on resume |
|----------|---------------------|
| `current-job.txt` | read at startup — points to the interrupted job |
| `execution.log` | **appended to** — entries from both runs are present; run boundaries are marked by the `=== Orchestrator: starting ===` header line |
| Level:TOP README `## Execution Log` table | **overwritten** — shows only the resumed run's invocations (starting from #1) |
| `run-metrics.json` | written on normal completion of the resumed portion only |
| `run-summary.md` | written on normal completion of the resumed portion only |

### Preserving the stalled run's execution log table

Before resuming, copy the Level:TOP pipeline README if you need the partial
invocation table:

```bash
cp <target>/project/tasks/.../build-1/README.md \
   <output>/stalled-run-build-README.md
```

### Cleaning stale output before resuming (`--clean-resume`)

If the pipeline stalled during ARCHITECT or IMPLEMENTOR, the output directory
may contain partial or incorrect output from the interrupted component. The
IMPLEMENTOR will read these stale files and spend tokens analysing and
rewriting them. Use `--clean-resume` to delete them before restarting:

```bash
python3 ai-builder/orchestrator/orchestrator.py \
    --target-repo <target> \
    --output-dir  <output> \
    --epic        main \
    --clean-resume
```

`--clean-resume` implies `--resume`. Before starting the main loop it runs
`_clean_for_resume`, which:

1. Reads the last role from `execution.log` (the `[ISO] ROLE/agent` lines
   written by `log_run`).
2. Applies the stall-during rules:

| Stalled role | Action |
|--------------|--------|
| `ARCHITECT` or `IMPLEMENTOR` | Delete OUTPUT_DIR items newer than the last `LEAF_COMPLETE_HANDLER` timestamp. If no LCH has ever run, delete all unprotected items. |
| `TESTER` | Leave output intact — a TESTER stall means the code was complete; deletion would be wasteful. |
| unknown / no prior run | No-op. |

The following names are always protected and never deleted:

```
runs/  current-job.txt  execution.log  run-metrics.json  run-summary.md
```

### Merging stalled and resumed execution logs

`execution.log` contains entries from both runs concatenated. The structured
files (`run-metrics.json`, the README table) only reflect the resumed portion.
No tooling exists to automatically produce a merged `run-metrics.json`
spanning both runs. Manual reconstruction is possible by parsing
`execution.log` — each run begins with a `=== Orchestrator: starting ===`
line that serves as the boundary.

---

## Key Constants

| Name | Value | Purpose |
|------|-------|---------|
| `TIMEOUT_MINUTES` | 5 | Per-role subprocess timeout |
| `MAX_ROLE_ITERATIONS` | 3 | Max consecutive self-routes before halting with error |
| `AGENTS` | dict | Maps role name → agent CLI name; populated from machine file |
| `ROUTES` | dict | Maps `(role, outcome)` → next role or `None`; populated from machine file |
| `ROLE_PROMPTS` | dict | Maps role name → prompt `Path` or `None` (dynamic); populated from machine file |
| `REPO_ROOT` | Path | Absolute path to the ai-builder repo root |
| `ROLES_DIR` | Path | `REPO_ROOT/ai-builder/orchestrator/machines/builder/roles/` — fallback location for role prompt files not specified in the machine JSON |
| `MACHINES_DIR` | Path | `orchestrator/machines/` — built-in machine file directory |
| `EXECUTION_LOG` | Path | `OUTPUT_DIR/execution.log` |
| `CURRENT_JOB_FILE` | Path | `OUTPUT_DIR/current-job.txt` (TM mode only) |

## Metrics State (main loop)

| Variable | Type | Purpose |
|----------|------|---------|
| `run` | `RunData` | Accumulates per-invocation records for the entire pipeline run |
| `build_readme` | `Path \| None` | Path to the Level:TOP pipeline-subtask README; target for live execution log updates |
| `role_counters` | `dict[str, int]` | Counts how many times each role has been invoked; used as the `role_counter` for `record_invocation` |

`run` is initialized before the loop with `task_name` derived from `description_from_job_path(initial_job_doc)`.
`build_readme` is set by `_find_level_top(initial_job_doc)` before the loop and lazily by `_find_level_top(job_doc)` on the first `HANDLER_SUBTASKS_READY` transition where it is still `None`.

---

## TM Mode Validation

In TM mode, before the main loop starts, the orchestrator validates that the
initial job document is a **PIPELINE-SUBTASK with `Level: TOP`**. If either
check fails, the orchestrator prints a diagnostic message and exits with code 1.

| Check | Error message |
|-------|---------------|
| `Task-type` must be `PIPELINE-SUBTASK` | `TM mode requires a PIPELINE-SUBTASK as the pipeline entry point` |
| `Level` must be `TOP` | `TM mode requires the pipeline entry point to have Level: TOP` |

Use `new-pipeline-build.sh` to create a correctly-structured entry point. Pointing
the orchestrator at a USER-TASK or a non-TOP pipeline-subtask is always an error.

---

## TM Mode Handlers

In TM mode two handler roles replace the old single `TASK_MANAGER` role:

| Role | Trigger | Purpose |
|------|---------|---------|
| `DECOMPOSE_HANDLER` | `ARCHITECT_DECOMPOSITION_READY` | Creates subtasks from the Components table; points pipeline at the first subtask |
| `LEAF_COMPLETE_HANDLER` | `TESTER_TESTS_PASS` | Marks the completed subtask done, advances to next subtask or halts |

### DECOMPOSE_HANDLER: ancestry chain context

Each child subtask's `## Context` is a **labelled ancestry chain** — one entry
per ancestor level, newest appended last. This prevents the flat-copy duplication
that occurs when context is copied verbatim at each descent.

```
### Level 2 — user-service
Build a user authentication service supporting OAuth2 and local login.

### Level 3 — handlers
Routes incoming HTTP requests to the store and middleware components.
```

A `depth` field in `task.json` tracks numeric nesting depth. The pipeline entry
point (Level:TOP) starts at `depth: 0`. DECOMPOSE_HANDLER sets
`depth = parent_depth + 1` on each child and appends a new labelled entry
(`### Level {child_depth} — {task_name}`) to the inherited chain.

Downstream agents receive the full ancestry chain in their job doc's `## Context`
without needing to traverse the task tree.

See `learning/pipeline-task-context-ancestry-chain.md` for full rationale.

Valid outcomes for each handler:

| Role | Outcomes |
|------|---------|
| `DECOMPOSE_HANDLER` | `HANDLER_SUBTASKS_READY`, `HANDLER_NEED_HELP` |
| `LEAF_COMPLETE_HANDLER` | `HANDLER_SUBTASKS_READY`, `HANDLER_ALL_DONE`, `HANDLER_STOP_AFTER`, `HANDLER_NEED_HELP` |

---

## Functions

### `load_state_machine(machine_file) -> (agents, routes, start_state, role_prompts)`

Loads and validates a JSON machine file. Returns four values used by the
orchestrator to drive the pipeline:

- `agents` — `{role: agent_cli_name}` dict
- `routes` — `{(role, outcome): next_role_or_None}` dict
- `start_state` — default entry role (overridable with `--start-state`)
- `role_prompts` — `{role: Path | None}` dict (`None` = dynamic generation)

Validation checks:
- All three top-level keys present (`start_state`, `roles`, `transitions`)
- `start_state` appears in `roles`
- All source roles in `transitions` appear in `roles`
- All next-role values (non-null) in `transitions` appear in `roles`

Relative prompt paths are resolved against `REPO_ROOT`.
Exits with code 1 on any validation failure.

---

### `build_prompt(role, job_doc, output_dir, handoff_history) -> str`

Constructs the full prompt sent to an agent for a given role invocation.

**DECOMPOSE_HANDLER / LEAF_COMPLETE_HANDLER:** prompts are built inline as
f-strings with deeply embedded runtime values (`TARGET_REPO`, `EPIC`,
`PM_SCRIPTS_DIR`, `output_dir`). Each handler has exactly one prompt with no
branching.

**Design decision — handler prompts stay inline:** Other roles have static
prompts because their instructions don't change at runtime. Handler prompts
embed runtime values (`TARGET_REPO`, `EPIC`, paths). Once a template variable
injection system exists (see task `7eec4a`), handlers can be extracted to
static files.

**All other roles:** checks `ROLE_PROMPTS[role]` first (set from machine file);
falls back to `ROLES_DIR/<ROLE>.md` if not set; falls back to a generic instruction
string if neither file exists.

**All roles:** appends `## Handoff Notes from Previous Agents` section
containing all prior handoff messages, separated by `---`.

Prompt ends with an instruction to emit `OUTCOME`, `HANDOFF`, and `DOCS`
fields.

---

### `parse_outcome(response) -> (outcome, handoff)`

Extracts `OUTCOME:` and `HANDOFF:` from the agent's response text using
regex. Returns `("UNKNOWN", "(no handoff provided)")` if either field is
missing. `DOCS:` parsing is not yet implemented — see `open-questions.md`.

---

### `log_run(role, agent, outcome, handoff) -> None`

Appends a timestamped record to `execution.log` with role, agent, outcome,
and handoff. Append-only — never overwrites prior entries.

---

### `_find_level_top(readme) -> Path | None`

Returns `readme` if the file exists and contains `| Level | TOP |` in its
metadata table, else `None`. Used to locate the Level:TOP pipeline-subtask
README that receives live execution log updates.

---

## Main Loop

```
current_role = "ARCHITECT" (always — handlers only run when routed to them)
job_doc      = --job path (non-TM mode)
             | current-job.txt contents if pre-seeded by Oracle (TM mode)
             | None if Oracle has not yet written current-job.txt (TM mode, first handler run)

run          = RunData(task_name, start=now)
build_readme = _find_level_top(initial_job_doc)

while current_role is not None:
    agent  = AGENTS[current_role]
    prompt = build_prompt(current_role, job_doc, OUTPUT_DIR, handoff_history)

    inv_start = now
    result = run_agent(agent, TIMEOUT_MINUTES, current_role, prompt, OUTPUT_DIR)
    inv_end = now

    if result.exit_code == 2: timeout  → halt (sys.exit 1)
    if result.exit_code == 1: error    → halt (sys.exit 1)

    outcome, handoff = parse_outcome(result.response)
    handoff_history.append(f"[{current_role}] {handoff}")
    log_run(current_role, agent, outcome, handoff)

    # Record invocation metrics
    role_counters[current_role] += 1
    metrics_mod.record_invocation(run, role, agent, role_counters[current_role],
        description_from_job_path(job_doc), inv_start, inv_end,
        result.tokens_in, result.tokens_out, result.tokens_cached, outcome)

    # Update live execution log in the Level:TOP README
    if build_readme is None:
        build_readme = _find_level_top(job_doc)
    if build_readme is not None:
        metrics_mod.update_task_doc(build_readme, run)

    if outcome.endswith("_NEED_HELP"): → halt (sys.exit 0, human required)
    if outcome not in ROUTES:          → halt (sys.exit 1, unrecognised outcome)

    # TM mode: read job path after a handler signals HANDLER_SUBTASKS_READY
    if current_role in ("DECOMPOSE_HANDLER", "LEAF_COMPLETE_HANDLER") and outcome == "HANDLER_SUBTASKS_READY":
        job_doc = Path(CURRENT_JOB_FILE.read_text().strip())
        if build_readme is None:
            build_readme = _find_level_top(job_doc)

    next_role = ROUTES.get((current_role, outcome))

    # Self-loop guard: increment counter if routing back to same role
    if next_role == current_role:
        role_iteration_counts[current_role] += 1
        if role_iteration_counts[current_role] >= MAX_ROLE_ITERATIONS:
            → halt (sys.exit 1, iteration limit reached)
    else:
        role_iteration_counts.pop(current_role)  # reset on role change

    current_role = next_role

# End of run
run.end = now
metrics_mod.write_run_summary(OUTPUT_DIR, run)
metrics_mod.write_run_metrics_json(OUTPUT_DIR, run)
metrics_mod.write_summary_to_readme(build_readme, run)
```

Any outcome ending in `_NEED_HELP` exits with code 0 (expected halt, not an
error). All other halts exit with code 1.

End-of-run writes only execute when the pipeline completes normally (exits the
`while` loop). Timeout, agent error, and `_NEED_HELP` halts exit before reaching
this block; `run-summary.md` and `run-metrics.json` are not written for those cases.

---

## File Reads and Writes

| Operation | File | When |
|-----------|------|------|
| Read | `--job` (job document) | TM and non-TM mode startup; in TM mode `--resume` reads `last-job.json` instead |
| Read | `ROLE_PROMPTS[role]` (from machine JSON) or `ROLES_DIR/<ROLE>.md` fallback | each `build_prompt()` call for AI roles |
| Write | `execution.log` | after every role run (append) |
| Write | `current-job.txt` | by `DECOMPOSE_HANDLER` or `LEAF_COMPLETE_HANDLER` after `HANDLER_SUBTASKS_READY` — internal handler comms; path to the next job README |
| Read | `current-job.txt` | by orchestrator after a handler emits `HANDLER_SUBTASKS_READY` — updates `job_doc` for downstream roles |
| Write | `last-job.json` | by orchestrator after each `HANDLER_SUBTASKS_READY` advance — `{"active_task": "/abs/path/to/task.json"}`; read by `--resume` to restore active task |
| Read/Write | Level:TOP `README.md` | after every invocation — `update_task_doc` rewrites the `## Execution Log` table |
| Write | `run-summary.md` | on pipeline completion (normal exit only) |
| Write | `run-metrics.json` | on pipeline completion (normal exit only) |
| Append | Level:TOP `README.md` | on pipeline completion — `write_summary_to_readme` appends `## Run Summary` |

**Oracle contract (TM mode):** before invoking the orchestrator, Oracle must:
1. Place the top-level task in `in-progress/` in the target repo's task system
2. Pass its README path via `--job path/to/README.md`

To resume a mid-run pipeline: `--resume` (reads `last-job.json`; no `--job` required).

---

## Design Notes

- `CLAUDECODE` env var is stripped before spawning subprocesses. The claude
  CLI unconditionally blocks startup when this variable is set (it detects
  a nested Claude Code session). Subprocesses use `-p` (non-interactive) so
  the concern doesn't apply, but the check is unconditional.
- `shutil.which()` resolves the full executable path at subprocess build time,
  working around PATH limitations when the orchestrator is called from
  environments where nvm-managed node paths are not inherited.
- The orchestrator is stateless between runs. All state lives in the output
  directory (`last-job.json`, `execution.log`) and the target repo's task
  system.
