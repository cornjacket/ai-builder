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
| `--request` | TM mode | Path to project request file passed to TASK_MANAGER |

`TM_MODE` is true when `--target-repo` is provided. The two modes are
mutually exclusive: `--job` is required in non-TM mode and ignored in TM mode.

---

## Key Constants

| Name | Value | Purpose |
|------|-------|---------|
| `TIMEOUT_MINUTES` | 5 | Per-role subprocess timeout |
| `AGENTS` | dict | Maps role name → agent CLI name (`claude` or `gemini`) |
| `ROUTES` | dict | Maps `(role, outcome)` → next role or `None` (halt) |
| `REPO_ROOT` | Path | Absolute path to the ai-builder repo root |
| `ROLES_DIR` | Path | `REPO_ROOT/roles/` — where role prompt files live |
| `EXECUTION_LOG` | Path | `OUTPUT_DIR/execution.log` |
| `CURRENT_JOB_FILE` | Path | `OUTPUT_DIR/current-job.txt` (TM mode only) |

---

## Functions

### `build_prompt(role, job_doc, output_dir, handoff_history) -> str`

Constructs the full prompt sent to an agent for a given role invocation.

**TASK_MANAGER:** prompt is built inline as an f-string. Detects first vs.
subsequent runs by checking whether `CURRENT_JOB_FILE` exists. First run
instructs TM to set up the task system and decompose the request. Subsequent
runs instruct TM to mark the completed task done and pick the next one.

**All other roles:** loads `roles/<ROLE>.md` as role instructions. Falls back
to a generic instruction string if the file does not exist.

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

## Main Loop

```
current_role = "TASK_MANAGER" (TM mode) or "ARCHITECT" (non-TM mode)
job_doc      = job document path (non-TM mode) or None (TM mode, set later)

while current_role is not None:
    agent  = AGENTS[current_role]
    prompt = build_prompt(current_role, job_doc, OUTPUT_DIR, handoff_history)
    result = run_agent(agent, TIMEOUT_MINUTES, current_role, prompt, OUTPUT_DIR)

    if result.exit_code == 2: timeout  → halt (sys.exit 1)
    if result.exit_code == 1: error    → halt (sys.exit 1)

    outcome, handoff = parse_outcome(result.response)
    handoff_history.append(f"[{current_role}] {handoff}")
    log_run(current_role, agent, outcome, handoff)

    if outcome == "NEED_HELP": → halt (sys.exit 0, human required)
    if outcome not in ROUTES:  → halt (sys.exit 1, unrecognised outcome)

    # TM mode: read job path after TM signals JOBS_READY
    if current_role == "TASK_MANAGER" and outcome == "JOBS_READY":
        job_doc = Path(CURRENT_JOB_FILE.read_text().strip())

    current_role = ROUTES.get((current_role, outcome))
```

`NEED_HELP` exits with code 0 (expected halt, not an error). All other
halts exit with code 1.

---

## File Reads and Writes

| Operation | File | When |
|-----------|------|------|
| Read | `--job` (job document) | non-TM mode startup |
| Read | `--request` (project request) | TM mode, passed to TASK_MANAGER prompt |
| Read | `roles/<ROLE>.md` | each `build_prompt()` call for non-TM roles |
| Read | `current-job.txt` | after TASK_MANAGER emits `JOBS_READY` |
| Write | `execution.log` | after every role run (append) |
| Read/Write | `current-job.txt` | written by TASK_MANAGER, read by orchestrator |

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
  directory (`current-job.txt`, `execution.log`) and the target repo's task
  system.
