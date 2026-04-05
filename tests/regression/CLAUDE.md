# Regression Test Guidelines

## Approval and safety

**Never start a regression run without explicit user approval.** Do not run
`reset.sh` or the pipeline unless the user has directly asked you to run the
regression in the current message. Completing a task or committing code does
not imply permission.

**Never start a regression run if one is already in progress.** Before running
`reset.sh`, check whether a pipeline is currently running by inspecting the
Level: TOP pipeline-subtask README in the target repo. `reset.sh` enforces
this automatically — it will abort if the current pipeline is incomplete. Do
not use `--force` unless you have confirmed the pipeline process is no longer
running.

---

## Step-by-step regression procedure

### 1. Check for a replay first

Before launching a live run, check whether a replay exists for this regression:

```bash
tests/regression/<name>/gold/  # look for a recorded replay
```

If a replay is available, run it instead — it is zero-cost (no AI invocations,
no tokens consumed). Live runs are only necessary when no replay exists or when
the change being verified cannot be validated by replay.

### 2. Record the run in the verification subtask README (if applicable)

If this run is tied to a user task, record the sandbox paths and pipeline task
ID in the verification subtask README (the subtask in `project/tasks/` tracking
this regression) under a `## Run` section. `reset.sh` creates the pipeline task
inside the target repo's own task system and prints the task ID at the end of
its output. Skip this step for runs with no associated task (e.g. routine health
checks):

```markdown
## Run

| Field         | Value                                      |
|---------------|--------------------------------------------|
| Run date      | YYYY-MM-DD                                 |
| Target        | `sandbox/regressions/<name>/target/`       |
| Output        | `sandbox/regressions/<name>/output/`       |
| Pipeline task | `<hex-id>-NNNN-<subtask-name>`             |
```

### 3. Run the regression

```bash
bash tests/regression/<name>/run.sh [--force]
```

`run.sh` always records. It handles reset, pipeline execution with
`--record-to`, archiving, gold tests, and push to `ai-builder-recordings`
in one shot. The run-history row is appended automatically — but Gold and
Notes are left blank for you to fill in.

Pass `--force` when overwriting an existing recording.

### 4. Fill in Gold and Notes on the last run-history row

`run.sh` appends the row but leaves Gold and Notes blank. After it
completes, fill them in:

```bash
bash tests/regression/lib/update-run-history.sh \
    --history tests/regression/<name>/runs/run-history.md \
    --gold    pass|fail \
    --notes   "<triggering-task-or-reason>"
```

- **Gold** is `pass` or `fail` based on the gold test result.
- **Notes** should reference the user task that triggered this run, if one
  exists (e.g. `8985d4-bug-pipeline-teardown-and-formatting`). If the run was
  not tied to a specific task — for example a routine health check — write a
  brief reason instead (e.g. `routine health check`, `weekly baseline`).

**Replay runs are never recorded in run-history.md.** The history tracks live
AI-invoked runs only. Recording replays would inflate the run count and
misrepresent token costs.

### 5. Commit the run-history row

Commit `run-history.md` after gold tests have completed — not before. A row
in the history represents a finished, verified run.

```bash
git add tests/regression/<name>/runs/run-history.md
git commit -m "Record <name> regression run N — gold <pass/fail>

Task: <hex-id>-<task-name>   ← omit if no associated task (e.g. routine health check)

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Regression suite layout

Each regression test lives in its own subdirectory:

```
tests/regression/<name>/
    run.sh         — full regression run: reset + pipeline + archive + gold + push
    reset.sh          — archives prior runs, sets up a fresh target repo (called by run.sh)
    test-replay.sh    — zero-cost replay of a previously recorded run
    gold/             — Go regression tests that validate the output
    runs/
        run-history.md — one row per live AI run (never replay runs)
    source/           — source files to document (doc regressions only)
```

Output and target repos are written to `sandbox/regressions/<name>/` (gitignored).
