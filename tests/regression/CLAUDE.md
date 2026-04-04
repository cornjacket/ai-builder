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

### 2. Create a pipeline-subtask under the feature task

Before running `reset.sh`, create a verification pipeline-subtask under the
parent USER-TASK that this regression is verifying:

```bash
README=$(project/tasks/scripts/new-pipeline-build.sh \
    --epic main --folder in-progress --parent <user-task-name> \
    | grep "^README:" | awk '{print $2}')
```

Note the fully-qualified subtask name printed by the script (e.g.
`aa9b29-0000-build-1`). This is the pipeline task reference used throughout
the rest of the procedure.

### 3. Record the run in the verification subtask README

After `reset.sh` completes, record the sandbox paths and pipeline task ID in
the verification subtask README under a `## Run` section:

```markdown
## Run

| Field         | Value                                      |
|---------------|--------------------------------------------|
| Run date      | YYYY-MM-DD                                 |
| Target        | `sandbox/regressions/<name>/target/`       |
| Output        | `sandbox/regressions/<name>/output/`       |
| Pipeline task | `<hex-id>-NNNN-<subtask-name>`             |
```

### 4. Run the regression

```bash
bash tests/regression/<name>/run.sh
```

### 5. Run gold tests immediately after the pipeline completes

Do not defer gold tests. Run them as soon as the pipeline finishes:

```bash
cd tests/regression/<name>/gold && go test -v -tags regression ./...
```

Record the result (pass/fail) before moving on.

### 6. Append a row to run-history.md

After gold tests complete, append a row to
`tests/regression/<name>/runs/run-history.md`:

```markdown
| N | YYYY-MM-DD | Xm Xs | in / out / cached | in / out / cached | in / out / cached | pass/fail | <subtask-name> — <brief note> |
```

- **Token counts** come from `run-metrics.json` in the output directory.
- **Gold column** is `pass` or `fail`.
- **Notes** must include the fully-qualified pipeline-subtask name (e.g.
  `8985d4-0007-verify-platform-monolith → aa9b29-0000-build-1`) so the row
  can be traced back to the task that triggered the run.

**Replay runs are never recorded in run-history.md.** The history tracks live
AI-invoked runs only. Recording replays would inflate the run count and
misrepresent token costs.

### 7. Commit the run-history row

Commit `run-history.md` after gold tests have completed — not before. A row
in the history represents a finished, verified run.

```bash
git add tests/regression/<name>/runs/run-history.md
git commit -m "Record <name> regression run N — gold <pass/fail>

Task: <hex-id>-<task-name>
Subtask: <hex-id>-NNNN-<subtask-name>

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Regression suite layout

Each regression test lives in its own subdirectory:

```
tests/regression/<name>/
    reset.sh          — archives prior runs, sets up a fresh target repo
    run.sh            — invokes the orchestrator
    gold/             — Go regression tests that validate the output
    runs/
        run-history.md — one row per live AI run (never replay runs)
    source/           — source files to document (doc regressions only)
```

Output and target repos are written to `sandbox/regressions/<name>/` (gitignored).
