# Task: add-stub-role-injection-for-pipeline-testing

| Field    | Value                                              |
|----------|----------------------------------------------------|
| Status   | draft                                              |
| Epic     | main                                               |
| Tags     | orchestrator, testing, regression                  |
| Parent   | —                                                  |
| Priority | MED                                                |

## Description

Add a stub injection mechanism to `orchestrator.py` that allows any role to
be replaced by a pre-scripted response during pipeline testing. This makes
it possible to drive the pipeline into specific states deterministically,
without relying on LLM behaviour.

**Motivation:**

The re-architecture path (`NEEDS_ARCHITECT`) and other conditional flows are
difficult to test with real agents — they depend on the LLM detecting a
problem and choosing the right outcome. Stub injection lets regression tests
script the exact sequence of outcomes and handoffs, then verify that the
orchestrator routes correctly, DOCUMENTER runs at the right points, and
pipeline state (task system, logs, artifacts) is correct at each step.

**Proposed interface:**

```
python3 ai-builder/orchestrator.py \
    --job path/to/job.md \
    --output-dir path/to/work \
    --stub IMPLEMENTOR:path/to/stub.json \
    --stub ARCHITECT:path/to/stub.json
```

`--stub ROLE:path` replaces the named role with a stub that replays
responses from the JSON file in sequence. If the stub runs out of scripted
responses, the orchestrator falls back to the real agent (or halts with an
error — TBD).

**Stub file format:**

```json
[
  {
    "outcome": "NEEDS_ARCHITECT",
    "handoff": "Function signature incompatible with acceptance criteria. See Design section.",
    "docs": "none"
  },
  {
    "outcome": "DONE",
    "handoff": "Implemented revised Compute(n) per updated design.",
    "docs": "Update leaf README: revised function signature is Compute(n int) ([]int, error)"
  }
]
```

Each entry corresponds to one invocation of the stubbed role. The stub
returns the scripted `outcome`, `handoff`, and `docs` values without
calling any LLM.

**Primary use case — testing the re-architecture path:**

1. Stub IMPLEMENTOR: first call returns `NEEDS_ARCHITECT`, second returns `DONE`
2. Real ARCHITECT runs twice (initial design, then revision)
3. Real DOCUMENTER hook runs after each ARCHITECT and IMPLEMENTOR call
4. Test verifies: correct routing, README updated after revision, TESTER passes

This validates the re-architecture wiring without depending on an LLM
discovering a planted design flaw.

**Secondary use cases:**

- Testing the `TESTER → FAILED → IMPLEMENTOR` loop with a controlled number
  of retries
- Testing `NEED_HELP` halt behaviour from any role
- Testing TM mode: stub TM to emit `JOBS_READY` with a pre-written job doc,
  bypassing the real TM's task system manipulation
- Exercising the DOCUMENTER hook in isolation by stubbing all other roles

## Documentation

Add `--stub` flag documentation to `ai-builder/README.md` (or equivalent
orchestrator docs) once implemented.

## Subtasks

<!-- When a subtask is finished, run complete-subtask.sh to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

The stub mechanism should be invisible to the rest of the orchestrator —
`run_agent()` in `agent_wrapper.py` is the right intercept point. If a stub
is registered for the current role, it replays the next scripted response
instead of spawning a subprocess.

Fallback behaviour when the stub runs out of responses is a design decision:
- Error and halt (safest — test author must script every invocation)
- Fall through to real agent (useful for partial stubs)
The default should probably be halt, with an explicit `"fallback": "real"`
option in the stub file if fall-through is wanted.
