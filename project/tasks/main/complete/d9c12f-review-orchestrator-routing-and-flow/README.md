# Task: review-orchestrator-routing-and-flow

| Field    | Value                |
|----------|----------------------|
| Status | complete |
| Epic     | main                 |
| Tags     | orchestrator, review |
| Parent   | —                    |
| Priority | HIGH                 |

## Description

Review the orchestrator code and documentation for correctness, consistency,
and staleness after the pipeline restructure (de4588). Fix all issues found.

---

### Known issues to fix

**Stale documentation:**

- `ai-builder/orchestrator/README.md` agents table lists all roles as `gemini`
  — they are all `claude` now. Also references `JOB-TEMPLATE.md` which was
  deleted in the restructure.
- `ai-builder/orchestrator/routing.md` agents section shows `gemini` for
  IMPLEMENTOR — stale.
- `ai-builder/orchestrator/README.md` references several files that may not
  exist: `open-questions.md`, `../oracle/README.md`, `job-format.md`.
  Verify each exists; remove or update stale references.

**DOCUMENTER hook — documented but not implemented:**

`routing.md` and `README.md` both describe a DOCUMENTER hook in detail
(trigger config, `DOCS:` field, hook logic). This hook does not exist in
`orchestrator.py`. Either:
- Remove the DOCUMENTER documentation until the feature is implemented, or
- Mark it clearly as "planned, not yet implemented" in the docs.

**TM prompt design inconsistency:**

All non-TM roles load their prompt from `roles/<ROLE>.md` (static) with
runtime context appended. The TASK_MANAGER prompt is a hardcoded f-string in
`build_prompt()` mixing static role definition with dynamic runtime values.
Decision needed: should TM follow the same pattern (static `roles/TASK_MANAGER.md`
+ dynamic context injected separately)? Document the decision either way.

---

### Review checklist

- [x] ROUTES table in code matches `routing.md` — no missing or extra entries
- [x] All outcomes emitted by each role are represented in ROUTES
- [x] `_NEED_HELP` handling correct (caught before ROUTES lookup, halts cleanly)
- [x] Iteration limit logic correct for self-routing outcomes (`ARCHITECT_NEEDS_REVISION`)
- [x] TM `current-job.txt` read-after-`TM_SUBTASKS_READY` handles edge cases
      (file missing, path invalid)
- [x] `--job` (non-TM mode) still works correctly after restructure
- [x] Stale docs fixed (agents table, JOB-TEMPLATE.md deleted, oracle ref removed)
- [x] DOCUMENTER documentation resolved (marked planned/unimplemented)
- [x] TM prompt design decision documented (orchestrator.md)

## Documentation

Update `ai-builder/orchestrator/README.md` and `routing.md` as needed.
If files referenced in README.md do not exist, remove the references.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [x] [201e52-remove-new-task-sh](201e52-remove-new-task-sh/)
<!-- subtask-list-end -->

## Notes

_None._
