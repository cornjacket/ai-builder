# Subtask: add-decomposition-regression-test

| Field    | Value                |
|----------|----------------------|
| Status   | —                    |
| Epic     | main             |
| Tags     | —             |
| Parent   | 8eea17-implement-decomposition-in-orchestrator           |
| Priority | —         |

## Description

Add a regression test for the decomposition pipeline using a small service
with 2-3 atomic components only. This validates the full decompose →
design → implement → test loop without requiring composite node handling.

**Test service:** a simple Go package with 2-3 clearly separable atomic
components (exact spec TBD — choose something where component boundaries
are unambiguous and the gold test is straightforward).

**Test structure** (mirrors fibonacci test layout):
```
tests/regression/<service-name>/
    gold/           # gold tests, hidden from pipeline agents
    work/           # pipeline working directory
        JOB-<service>.md.template
        .gitignore
    reset.sh
    README.md
```

**What the test verifies:**
1. ARCHITECT produces a valid component table (decompose pass)
2. TM creates correct subtasks from the table
3. ARCHITECT designs each component (design passes)
4. IMPLEMENTOR implements each component
5. TESTER passes for each component
6. TM signals `ALL_DONE` after all subtasks complete
7. Gold test suite passes against the assembled output

**Composite node handling is explicitly out of scope** — that is a subsequent
regression test once the atomic path is stable.

## Subtasks

<!-- When a subtask is finished, run complete-subtask.sh to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [x] ceca3e-create-test-scaffold
- [x] b7f3a1-write-job-document-template
- [x] e2d4c8-write-gold-test-suite
- [x] f9a5b2-run-pipeline-and-verify
<!-- subtask-list-end -->

## Notes

This is the last subtask — all other subtasks must be complete and verified
before the regression test can be written and run.
