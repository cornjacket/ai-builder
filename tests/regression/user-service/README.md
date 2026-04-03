# Regression Test: User Service

Verifies that the decomposition pipeline correctly decomposes a service-level
job into atomic components, designs and implements each one, and produces a
working HTTP CRUD service.

---

## Directory Structure

```
user-service/
    build-spec.md          # service specification fed to the pipeline
    reset.sh               # reset workspace to initial state before any run
    record.sh              # run the pipeline live and capture a recording
    test-replay.sh         # replay a recording and verify the result
    gold/                  # gold HTTP behavioural tests (never visible to agents)
        gold_test.go
    component-tests/       # per-invocation snapshot fixtures
    runs/                  # archived execution logs from past runs
        run-history.md     # one-line summary per run
        last_run -> ...    # symlink to most recent run directory
```

The regression workspace lives at `sandbox/regressions/user-service/` (one
level up from this directory). It is created by `reset.sh` and excluded from
git. The recording git repo is rooted there:

```
sandbox/regressions/user-service/
    target/          # fresh task repo, recreated on every reset
    output/          # pipeline output (Go source, execution.log, etc.)
    responses/       # pre-recorded AI responses (inv-NN-ROLE.txt)
    recording.json   # recording manifest
```

---

## Typical Workflows

### Running the replay regression test (zero AI cost)

This is the standard way to run the regression. It uses a pre-recorded
pipeline run stored in `sandbox/regressions/user-service/` (or fetched from
the remote if absent) and replays it without calling the AI.

```bash
bash tests/regression/user-service/test-replay.sh
```

What it does:
1. Ensures a recording is available locally (fetches from remote if needed)
2. Resets the workspace with the recorded task hex ID pinned so all paths match
3. Replays the pipeline (`--replay-from`) — no AI calls, handlers re-run live
4. Verifies the routing path matches the recording (same role/outcome sequence)
5. Verifies output artifacts and task structure match the recording snapshot

### Re-recording (after prompt changes or a new feature)

Run this when role prompts change or the pipeline behaviour changes and you
want to capture a new golden recording.

```bash
bash tests/regression/user-service/record.sh [--force]
```

`--force` is required if a recording already exists locally. The script
resets the workspace, runs the full pipeline live (costs AI tokens), pushes
the recording to the remote, and prints a summary.

After re-recording, run `test-replay.sh` once to confirm the new recording
replays cleanly.

### Manual live run (no recording)

```bash
bash tests/regression/user-service/reset.sh
JOB=$(cat sandbox/regressions/user-service/output/current-job.txt)
python3 ai-builder/orchestrator/orchestrator.py \
    --job           "$JOB" \
    --target-repo   sandbox/regressions/user-service/target \
    --output-dir    sandbox/regressions/user-service/output \
    --epic          main \
    --state-machine ai-builder/orchestrator/machines/builder/default.json
```

### Gold HTTP behavioural tests

After any live run (recording or manual), verify the assembled service:

```bash
cd tests/regression/user-service/gold && go test -tags regression ./...
```

---

## What This Tests

The full decomposition pipeline loop:

1. **ARCHITECT** (decompose) — reads the task spec, decomposes into components
2. **DECOMPOSE_HANDLER** — creates component subtasks, queues the first
3. **ARCHITECT** (design) — designs the component
4. **IMPLEMENTOR** — implements it
5. **TESTER** — builds and tests it
6. **LEAF_COMPLETE_HANDLER** — marks done, advances to next component
7. Steps 3–6 repeat for each component
8. **LEAF_COMPLETE_HANDLER** signals `HANDLER_ALL_DONE` when all done

The replay test verifies both the routing sequence and the output artifacts
(Go source files, task tree structure including completed subtask X- renames,
component READMEs with design/acceptance criteria).

---

## Further Reading

- [`ai-builder/orchestrator/record-replay.md`](../../../ai-builder/orchestrator/record-replay.md) — full reference for `--record-to`, `--replay-from`, snapshot comparison, and prompt drift
