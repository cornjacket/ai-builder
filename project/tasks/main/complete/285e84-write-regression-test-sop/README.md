# Task: write-regression-test-sop

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status | complete |
| Epic        | main               |
| Tags        | regression-test, docs, process |
| Priority    | MED                            |

## Goal

Write a guideline/SOP document at `tests/regression/README.md` covering how
to create, structure, and run regression tests for the ai-builder pipeline.

## Context

The regression test suite is growing and the process for creating tests is
currently implicit. The platform-monolith test revealed that a bad spec was
submitted to the pipeline without Oracle review, resulting in a wasted run.
A clear SOP would prevent this.

**Sections to cover:**

1. **Purpose** — what regression tests verify (pipeline correctness, not just
   code correctness); each test exercises a specific pipeline capability
   (flat atomic, single-level decomposition, multi-level decomposition, etc.)

2. **Directory structure** — standard layout:
   - `reset.sh` — sets up sandbox target repo and output dir
   - `gold/` — gold tests committed to the repo; never visible to pipeline agents
   - `README.md` — test documentation, run instructions, architecture diagram

3. **Build target location** — generated code goes to `sandbox/<test-name>-output/`;
   why sandbox/ and not /tmp (tracked in git, survives sessions)

4. **Gold tests** — purpose of the gold/ separation (TESTER derives its own
   tests from acceptance criteria; gold tests independently verify behaviour
   against the spec); build tag `regression`; how to run them

5. **reset.sh contract** — what every reset.sh must do: create fresh target
   repo, install task system, create USER-TASK boundary, create PIPELINE-SUBTASK
   entry point with Level=TOP, write spec to README, point current-job.txt

6. **Spec review checklist** — Oracle must review the build spec (the job doc
   in reset.sh) before running the pipeline; checklist items:
   - Architecture name matches the actual structure described
   - All required endpoints/interfaces are explicitly listed
   - Language, port, storage requirements are unambiguous
   - Testing requirements (unit, integration, e2e) are explicitly stated
   - The spec has been read end-to-end by the Oracle before submission

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [x] [09eb14-oracle-review-regression-test-sop](09eb14-oracle-review-regression-test-sop/)
<!-- subtask-list-end -->

## Notes

_None._
