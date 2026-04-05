# Task: pipeline-acceptance-spec-writer

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status | in-progress |
| Epic        | main               |
| Tags        | —               |
| Priority    | HIGH        |
| Category    | acceptance-spec        |
| Created     | 2026-04-03            |
| Completed   | —                      |
| Next-subtask-id | 0020 |

## Goal

Add an ACCEPTANCE_SPEC_WRITER stage to the builder pipeline that anchors the
API contract from the build spec before any decomposition or implementation
begins. This prevents AI-introduced drift in field names, endpoint coverage,
and status codes as the spec passes through multiple ARCHITECT transformations.

**Work in a new worktree** — this task touches the state machine, orchestrator,
ARCHITECT prompts, and documentation broadly.

## Context

**Root cause discovered during `8985d4-0007-verify-platform-monolith`:**
The gold tests failed on 5 IAM API tests that the pipeline's own TESTER had
passed. Investigation showed the ARCHITECT drifted from the build spec:
- Changed `roleId` → `role_id`, `userId` → `user_id`, `permission` → `role`
- Omitted `GET /roles` entirely from acceptance criteria
- Invented endpoints not in the spec (`DELETE /roles/{id}`)
- Changed status codes (spec: 200/201, ARCHITECT produced: 204)

The ARCHITECT prompt already instructs: *"Do not paraphrase or abbreviate
field names — copy them exactly."* The AI did not follow this reliably.

The TESTER passed because it runs the IMPLEMENTOR's tests, which were written
against the ARCHITECT's drifted acceptance criteria — not the original spec.
The gold tests are the only human-authored tests and caught the failures.

**Proposed solution — ACCEPTANCE_SPEC_WRITER stage:**

1. **New state: `ACCEPTANCE_SPEC_WRITER`** — runs once, immediately before the
   initial TOP ARCHITECT decompose. Reads the `## Goal` and `## Context` from
   the build spec and writes two files to the output dir:
   - `acceptance-spec.md` — human-readable, all endpoints with exact field
     names, status codes, request/response schemas, copied verbatim
   - `acceptance-spec.json` — machine-readable version of the same; used by
     the spec coverage checker

2. **Update DECOMPOSE ARCHITECT prompt** — when writing component descriptions,
   require the ARCHITECT to reference `acceptance-spec.md` for any HTTP
   component. Field names must match the spec exactly. This prevents drift
   during decomposition where sub-component ARCHITECTs currently work from
   summaries of summaries.

3. **Update TOP integrate ARCHITECT prompt** — require it to read
   `acceptance-spec.md` and explicitly reconcile its acceptance criteria
   against every endpoint listed. Flag any gaps before emitting the response.

4. **New internal agent: spec coverage checker** — after IMPLEMENTOR at the
   TOP integrate level, before TESTER runs, scan the generated test files
   against `acceptance-spec.json`. Fail fast with a coverage report if any
   endpoint is untested. This is a deterministic check — no AI involved.

**Why two passes:**
- Pass 1 (ACCEPTANCE_SPEC_WRITER): anchors the spec early, before any
  implementation, from the original build spec language
- Pass 2 (TOP integrate ARCHITECT + coverage checker): independently
  verifies that the generated tests cover every spec item

**Affected components:**
- `ai-builder/orchestrator/machines/builder/default.json` — new state
- `ai-builder/orchestrator/agents/builder/` — new ACCEPTANCE_SPEC_WRITER agent
- `ai-builder/orchestrator/machines/builder/roles/ARCHITECT.md` — updated prompts
- `ai-builder/orchestrator/` — new spec coverage checker agent
- All builder regression gold tests — may need updating
- All documentation for the builder pipeline and ARCHITECT role

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [x] [X-f5f7b8-0001-define-acceptance-spec-format](X-f5f7b8-0001-define-acceptance-spec-format/)
- [x] [X-f5f7b8-0002-add-acceptance-spec-writer-agent](X-f5f7b8-0002-add-acceptance-spec-writer-agent/)
- [x] [X-f5f7b8-0003-update-state-machine](X-f5f7b8-0003-update-state-machine/)
- [x] [X-f5f7b8-0004-persist-active-role-for-resume](X-f5f7b8-0004-persist-active-role-for-resume/)
- [x] [X-f5f7b8-0005-update-architect-prompts](X-f5f7b8-0005-update-architect-prompts/)
- [x] [X-f5f7b8-0006-add-spec-coverage-checker](X-f5f7b8-0006-add-spec-coverage-checker/)
- [ ] [f5f7b8-0007-re-record-user-service-regression](f5f7b8-0007-re-record-user-service-regression/)
- [ ] [f5f7b8-0008-verify-gold-tests](f5f7b8-0008-verify-gold-tests/)
- [ ] [f5f7b8-0009-update-affected-documentation](f5f7b8-0009-update-affected-documentation/)
<!-- subtask-list-end -->

## Notes

_None._
