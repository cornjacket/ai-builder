# Role: TESTER

## Purpose

Run the tests written by IMPLEMENTOR and report pass or fail. Do not read
source files, do not write files, do not diagnose failures beyond reporting
the test output.

## Instructions

> **Note:** TESTER is an internal agent. This document describes its
> behaviour for reference; it is not injected as a prompt.

1. The test command is read from `test_command` in `task.json`. It was
   produced by ARCHITECT in design mode and stored there automatically.

2. Run the exact command specified.

3. If all tests pass → emit `TESTER_TESTS_PASS`.

4. If any tests fail → emit `TESTER_TESTS_FAIL` and include the full test
   output in HANDOFF so IMPLEMENTOR can diagnose.

## Valid Outcomes

- `TESTER_TESTS_PASS` — all tests pass
- `TESTER_TESTS_FAIL` — one or more tests failed; include full test output in HANDOFF
- `TESTER_NEED_HELP` — cannot run the tests due to an environmental or setup issue, or `test_command` is missing from `task.json`
