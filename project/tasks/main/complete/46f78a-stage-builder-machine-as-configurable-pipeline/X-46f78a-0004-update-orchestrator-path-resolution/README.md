# Task: update-orchestrator-path-resolution

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 46f78a-stage-builder-machine-as-configurable-pipeline             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Update `orchestrator.py` so its `ROLES_DIR` fallback and `--state-machine`
default (if any) reflect the new paths. Verify the full unit test suite and
a smoke import of the updated machine JSON pass cleanly.

## Context

### Changes to `orchestrator.py`

**`ROLES_DIR` fallback (line 114):**
```python
# Before
ROLES_DIR = REPO_ROOT / "roles"

# After
ROLES_DIR = REPO_ROOT / "ai-builder" / "roles"
```

The fallback is only reached if a role has no explicit `"prompt"` field in the
machine JSON and is not an internal agent. In practice, all roles in the builder
machine have either an explicit prompt path or `"prompt": null`. The fallback
is a safety net and should now point to the new top-level roles directory.

### Verification steps

1. `python3 -m unittest discover -s tests/unit` — all 60 tests pass
2. Confirm `load_state_machine("machines/builder/default.json")` loads without
   error and resolves all prompt paths to files that exist:
   ```python
   from orchestrator_loader import load_state_machine  # or equivalent
   # prompt paths should resolve to existing files
   ```
3. Grep for any remaining references to the old paths:
   ```bash
   grep -rn '"roles/' ai-builder/orchestrator/machines/
   grep -rn 'REPO_ROOT / "roles"' ai-builder/orchestrator/orchestrator.py
   ```
   Both should return nothing.

### Regression tests

Check that regression test `reset.sh` scripts and any `--state-machine` flags
in component test `run.sh` scripts have been updated (these are covered in
subtask 0003, but verify here that orchestrator.py accepts the new path without
error).

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
