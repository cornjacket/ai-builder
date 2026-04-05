# spec_coverage_checker.py

`SpecCoverageCheckerAgent` — deterministic internal agent. Runs after
`DOCUMENTER_POST_IMPLEMENTOR`, before `TESTER`. Verifies that generated test
files cover every endpoint listed in `acceptance-spec.json`.

## run(job_doc, output_dir, **kwargs)

**Inputs:**
- `output_dir: Path` — pipeline output directory for the current component

**Reads:**
- `output_dir/acceptance-spec.json` — endpoint list produced by
  ACCEPTANCE_SPEC_WRITER; if absent the agent is a no-op

**Scans:**
- All `*_test.go`, `*_test.py`, `*.test.ts`, `*.test.js`, `*.spec.ts`,
  `*.spec.js` files found recursively under `output_dir`

**Coverage check:**
For each endpoint in `acceptance-spec.json`, the agent searches all test file
content for the endpoint path using a regex. Path parameters (`{id}`) are
converted to a one-segment wildcard (`[^/"'\s]+`) so that `/roles/{id}`
matches `/roles/123` in test code. No AST parsing — string/regex only.

**Returns `AgentResult` with:**

| Outcome | Condition |
|---------|-----------|
| `SPEC_COVERAGE_CHECKER_PASS` | All endpoints covered, or no spec file, or empty endpoints array |
| `SPEC_COVERAGE_CHECKER_FAIL` | One or more endpoints not found in test files |

On `FAIL`, the HANDOFF lists every uncovered endpoint by method and path.

## No-op conditions

The agent is a no-op (emits `PASS` immediately) when:
- `acceptance-spec.json` does not exist in `output_dir` — this is the normal
  case for all non-integrate components, which write to a subdirectory
- `acceptance-spec.json` exists but has an empty `endpoints` array

## TOP integrate detection

The spec files are written to the TOP output directory. The `integrate-<scope>`
component uses `source_dir: "."` and therefore shares the same `output_dir` as
the TOP level. All other components use a subdirectory and will not have
`acceptance-spec.json` present — making the no-op check the natural detection
mechanism.

## State machine

Registered in `machines/builder/default.json` between
`DOCUMENTER_POST_IMPLEMENTOR` and `TESTER`.
