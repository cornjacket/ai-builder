# Subtask: design-pipeline-regression-test

| Field    | Value                |
|----------|----------------------|
| Status   | —                    |
| Epic     | main             |
| Tags     | oracle, orchestrator, testing             |
| Parent   | 37a660-design-oracle-and-pipeline-phases           |
| Priority | MED         |

## Description

Design and implement an orchestrator-level regression test that exercises the
full PM→ARCHITECT→IMPLEMENTOR→TESTER pipeline end-to-end with a known request
and verifiable output.

Unlike `tests/regression/template-setup/` (which tests scripts without running
agents), this test actually runs AI agents and verifies what they produced
against predefined constraints.

**Test structure (mirrors fibonacci):**

```
tests/regression/pipeline-e2e/
    request.md           — predefined project request with explicit constraints
    gold/                — gold verifier (never visible to pipeline agents)
        verify.sh        — runs against work/ output, exits 0 if constraints met
    work/                — pipeline working directory (gitignored except reset state)
        project/tasks/   — task system populated by PM during planning
    reset.sh             — wipes work/ to initial state
    README.md
```

**Test flow:**
1. Oracle (or test harness) submits `request.md` to the pipeline with PM mode
2. PM runs Planning phase — creates task tree in `work/project/tasks/`
3. Human review step is skipped (automated) — plan is accepted as-is
4. PM runs Implementation phase — ARCHITECT → IMPLEMENTOR → TESTER per subtask
5. Gold verifier runs against `work/` output and checks:
   - All tasks in the plan were completed
   - Generated artifacts satisfy the constraints in `request.md`
   - Behaviour matches expected outputs

**Design questions to resolve:**

- What is the simplest request that exercises the full pipeline meaningfully?
  (Something deterministic enough to verify, complex enough to require planning)
- How is the human review step handled in an automated test? Options:
  - Skip it entirely (PM auto-approves its own plan)
  - A fixed plan injected as a fixture (bypasses PM planning)
  - A `--auto-approve` flag on the Oracle
- How does the gold verifier know what to check? Constraints must be
  explicit in `request.md` and machine-checkable in `verify.sh`
- Should this test be part of CI, or run manually due to AI agent cost?

## Notes

Depends on the Oracle and N-phase pipeline being sufficiently mature.
The fibonacci test is the structural model to follow.
