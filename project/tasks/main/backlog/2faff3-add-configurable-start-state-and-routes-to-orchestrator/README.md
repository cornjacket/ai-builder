# Task: add-configurable-start-state-and-routes-to-orchestrator

| Field    | Value                                        |
|----------|----------------------------------------------|
| Status   | backlog                                      |
| Epic     | main                                         |
| Tags     | orchestrator, pipeline, flexibility          |
| Parent   | —                                            |
| Priority | MED                                          |

## Description

Add two command-line options to the orchestrator:

- `--start-state <ROLE>` — the role to begin the pipeline at, overriding
  the current hardcoded default of `ARCHITECT`
- `--routes <file.json>` — path to a JSON file defining the transition
  state diagram, overriding the hardcoded `ROUTES` dict

Together these decouple the pipeline's execution model from its
implementation, making it usable for purposes beyond the current
ARCHITECT → IMPLEMENTOR → TESTER → TASK_MANAGER flow.

### `--start-state`

Allows the caller to specify which role the pipeline begins with:

```bash
# Cold-start / --request workflow: TM bootstraps task system from request file
python3 orchestrator.py \
    --target-repo ~/my-app \
    --output-dir  ~/my-app/project/pipeline-output \
    --start-state TASK_MANAGER \
    --request     ~/my-app/REQUEST.md

# Resume from TESTER to re-run verification against existing implementation
python3 orchestrator.py \
    --job        tests/regression/fibonacci/work/JOB-fibonacci-demo.md \
    --output-dir tests/regression/fibonacci/work \
    --start-state TESTER
```

Must validate that the requested role exists in `AGENTS`.

### `--routes <file.json>`

Allows the caller to supply an alternative transition state diagram as a
JSON file, replacing the hardcoded `ROUTES` dict. Format:

```json
{
  "ARCHITECT":   { "DONE": "IMPLEMENTOR", "NEED_HELP": null },
  "IMPLEMENTOR": { "IMPLEMENTATION_DONE": "TESTER", "NEEDS_ARCHITECT": "ARCHITECT", "NEED_HELP": null },
  "TESTER":      { "TESTS_PASS": null, "TESTS_FAIL": "IMPLEMENTOR", "NEED_HELP": null }
}
```

When `--routes` is not provided, the orchestrator uses its current
hardcoded defaults (TM mode or non-TM mode routes as appropriate).

### Restoring `--request` with `--start-state`

The `--request` flag was originally designed for a "cold start" workflow:
the orchestrator would start at TASK_MANAGER, which would read the request
file, install the task system, decompose the request into tasks, and create
the first job document.

This workflow broke when the pipeline was changed to always start at
ARCHITECT (so that Oracle — not TM — is responsible for bootstrapping).
With `--start-state TASK_MANAGER`, the cold-start path is restored as an
explicit opt-in, while the Oracle-driven path remains the default
(`--start-state ARCHITECT`).

This is also useful for testing: a test can start the pipeline at any
role with a known pre-populated state, without running the full pipeline
from the beginning.

## History

- The orchestrator originally started at `TASK_MANAGER` in TM mode and
  `ARCHITECT` in non-TM mode. TM was responsible for bootstrapping the
  task system from a `--request` file on first run.
- This was changed to always start at `ARCHITECT` because Oracle —
  not TM — is the entity responsible for bootstrapping. Oracle pre-seeds
  `current-job.txt` before invoking the orchestrator.
- As a result, the `--request` / first-run TM path became dead code:
  TM is never the starting role, so the request-driven bootstrap never
  runs.
- The `is_first_run` check in the TM prompt (`not CURRENT_JOB_FILE.exists()`)
  is now unreachable — TM only runs when routed from ARCHITECT
  (`COMPONENTS_READY`) or TESTER (`TESTS_PASS`).
- `--start-state` restores the cold-start path as an explicit option
  rather than an implicit default.

## Documentation

Update `ai-builder/orchestrator/orchestrator.md` with the new flags,
usage examples, and the routes JSON format.

## Subtasks

<!-- When a subtask is finished, run complete-subtask.sh to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

Related: `3cbd2e-702059-add-start-role-flag-to-orchestrator` (subtask of
`8eea17`) covers a narrower `--start-role` flag for resume and targeted
testing. This task supersedes that one — `--start-state` is the same
feature with a better name and a clearer rationale. When this task is
implemented, `3cbd2e` should be closed as superseded.
