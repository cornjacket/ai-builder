# Regression Test Guidelines

## Recording a regression run

After running `reset.sh` and before starting the pipeline, record the sandbox
paths and pipeline task ID in the **current verification subtask README** (the
subtask in `project/tasks/` that you are working on to verify this regression)
under a `## Run` section:

```markdown
## Run

| Field | Value |
|---|---|
| Run date | YYYY-MM-DD |
| Target | `sandbox/regressions/<name>/target/` |
| Output | `sandbox/regressions/<name>/output/` |
| Pipeline task | `<hex-id>-<name>` |
```

The pipeline task ID is printed by `reset.sh` at the end of its output.
This pointer lets you navigate from the user-task in `project/tasks/` directly
to the sandbox without searching.

Apply this convention retroactively to any in-progress regression subtask you
pick up.

## Running a regression

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

## Regression suite layout

Each regression test lives in its own subdirectory:

```
tests/regression/<name>/
    reset.sh          — archives prior runs, sets up a fresh target repo
    run.sh            — invokes the orchestrator
    gold/             — Go regression tests that validate the output
    source/           — source files to document (doc regressions only)
```

Output and target repos are written to `sandbox/regressions/<name>/` (gitignored).
