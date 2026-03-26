# user-service Component Tests

Single-step regression tests for the user-service pipeline. Each test
isolates one agent plus its downstream internal handlers, using a saved
"gold state" snapshot (task tree + output directory + `handoff-state.json`)
as the starting point.

---

## What this tests

The user-service pipeline exercises **single-level decomposition**: one
ARCHITECT decomposes the TOP task into 3 components, then each component is
built atomically (ARCHITECT → IMPLEMENTOR → TESTER), and finally an integrate
step wires everything together.

Component tests let you run any slice of this chain in isolation — without
running the full pipeline from scratch — by restoring a pre-captured sandbox
state and running one step of the orchestrator.

---

## Test steps

| Step | Gold state captures… | run.sh tests… | Expected outcome |
|------|----------------------|---------------|-----------------|
| `01-initial` | after `reset.sh`, before any agent runs | ARCHITECT (decompose) → DECOMPOSE\_HANDLER | `HANDLER_STOP_AFTER` |
| `02-after-decompose` | after decompose; 3 component subtasks created | ARCHITECT (store) → IMPLEMENTOR → TESTER → LCH | `HANDLER_STOP_AFTER` |
| `03-after-component-1` | after `store` component fully built | ARCHITECT (handlers) → IMPLEMENTOR → TESTER → LCH | `HANDLER_STOP_AFTER` |
| `04-after-component-2` | after `handlers` component fully built | ARCHITECT (integrate) → IMPLEMENTOR → TESTER → LCH | `HANDLER_ALL_DONE` |

`HANDLER_STOP_AFTER` is triggered by `stop-after: true` in the current
component's `task.json`. `HANDLER_ALL_DONE` is the natural end of the pipeline
(integrate is the last component so the pipeline completes normally).

---

## How stop-after works

Each gold state has `stop-after: true` set in the **relevant** task's
`task.json` before capture:

- **Step 01** (`01-initial`): `stop-after: true` in the Level:TOP `build-1`
  task.json. After ARCHITECT decomposes and DECOMPOSE\_HANDLER creates subtasks,
  DECOMPOSE\_HANDLER checks the parent task's `stop-after` flag and emits
  `HANDLER_STOP_AFTER` instead of advancing to the first component.

- **Steps 02–03**: `stop-after: true` in the current component's `task.json`.
  After TESTER passes, LEAF\_COMPLETE\_HANDLER calls `on-task-complete.sh`
  which calls `check-stop-after.sh` and emits `STOP_AFTER` → `HANDLER_STOP_AFTER`.

- **Step 04** (integrate): no `stop-after` needed — integrate is the last
  component, so LCH naturally emits `HANDLER_ALL_DONE`.

---

## Running a test step

```bash
# Run one step (requires gold state to be bootstrapped first)
tests/regression/user-service/component-tests/run.sh \
    --step           01-initial \
    --start-state    ARCHITECT \
    --expected-outcome HANDLER_STOP_AFTER
```

Each step uses `--resume` internally (bypasses Level:TOP validation for
mid-pipeline starts) and auto-loads `handoff-state.json` from the restored
output directory.

---

## Bootstrapping gold states (one-time setup)

Gold states are committed to the repo inside `steps/*/gold/`. They are
created once from a successful full pipeline run and then serve as the
baseline for all future single-step tests.

### Step 01-initial

```bash
# 1. Clean reset
tests/regression/user-service/reset.sh

# 2. Inject stop-after into build-1's task.json
python3 -c "
import json, glob
files = glob.glob('sandbox/user-service-target/project/tasks/main/in-progress/*/*/task.json')
# Find the Level:TOP task
for f in files:
    d = json.load(open(f))
    if d.get('level') == 'TOP':
        d['stop-after'] = True
        open(f,'w').write(json.dumps(d, indent=2) + '\n')
        print('Set stop-after in', f)
        break
"

# 3. Capture the initial state (before any orchestrator run)
tests/regression/user-service/component-tests/capture.sh --step 01-initial
```

### Step 02-after-decompose

```bash
# 4. Run the orchestrator (it will stop after DECOMPOSE_HANDLER)
python3 ai-builder/orchestrator/orchestrator.py \
    --target-repo   sandbox/user-service-target \
    --output-dir    sandbox/user-service-output \
    --epic          main \
    --state-machine ai-builder/orchestrator/machines/default.json

# 5. Inject stop-after into the first component's task.json
python3 -c "
import json, glob, pathlib
# Find component subtasks (depth > 1, no 'last-task': True)
files = glob.glob('sandbox/user-service-target/project/tasks/main/in-progress/**/task.json', recursive=True)
components = [(f, json.load(open(f))) for f in files]
# First component: depth > 1, not last-task, not integrate
for f, d in sorted(components, key=lambda x: x[0]):
    if d.get('depth', 0) > 1 and d.get('name') not in ('integrate', None) and not d.get('last-task'):
        d['stop-after'] = True
        open(f,'w').write(json.dumps(d, indent=2) + '\n')
        print('Set stop-after in', f)
        break
"

# 6. Capture
tests/regression/user-service/component-tests/capture.sh --step 02-after-decompose
```

### Steps 03 and 04

Continue the chain:

```bash
# 7. Run component-1 step (stops at HANDLER_STOP_AFTER)
tests/regression/user-service/component-tests/run.sh \
    --step 02-after-decompose --start-state ARCHITECT \
    --expected-outcome HANDLER_STOP_AFTER

# 8. Inject stop-after into component-2's task.json in the sandbox
python3 -c "
import json, glob
files = glob.glob('sandbox/user-service-target/project/tasks/main/in-progress/**/task.json', recursive=True)
for f in files:
    d = json.load(open(f))
    if d.get('depth', 0) > 1 and d.get('name') not in ('integrate', None) and not d.get('last-task') and not d.get('stop-after'):
        d['stop-after'] = True
        open(f,'w').write(json.dumps(d, indent=2) + '\n')
        print('Set stop-after in', f)
        break
"

# 9. Capture
tests/regression/user-service/component-tests/capture.sh --step 03-after-component-1

# 10. Similarly bootstrap step 04-after-component-2 (integrate has no stop-after needed)
tests/regression/user-service/component-tests/run.sh \
    --step 03-after-component-1 --start-state ARCHITECT \
    --expected-outcome HANDLER_STOP_AFTER
tests/regression/user-service/component-tests/capture.sh --step 04-after-component-2
```

---

## Directory structure

```
component-tests/
    README.md         — this file
    capture.sh        — saves current sandbox state to steps/<step>/gold/
    run.sh            — restores gold state, runs one orchestrator step
    steps/
        01-initial/
            gold/
                target-tasks/   — project/tasks/ snapshot
                output/         — output dir snapshot (current-job.txt, etc.)
                                  (no handoff-state.json for step 01)
        02-after-decompose/
            gold/
                target-tasks/
                output/
                handoff-state.json
        03-after-component-1/
            gold/ ...
        04-after-component-2/
            gold/ ...
```

Gold states are committed to the repo. Generated Go code in `output/` is
included in the snapshot (needed by IMPLEMENTOR and TESTER steps).

---

## Key constraints

- **Do not run two component tests concurrently.** They share the same sandbox
  paths (`sandbox/user-service-target/`, `sandbox/user-service-output/`).
- **Steps are stateful.** run.sh always wipes and restores the sandbox before
  running. The output after a run reflects only that step's work.
- **Gold states are machine-specific.** Task directory names contain timestamps
  that are captured verbatim. `output_dir` fields in `task.json` are absolute
  paths. Gold states must be bootstrapped on the machine where tests will run,
  or the absolute paths must be rebased (not currently automated).
