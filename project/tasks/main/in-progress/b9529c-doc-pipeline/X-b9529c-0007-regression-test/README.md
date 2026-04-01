# Task: regression-test

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | b9529c-doc-pipeline             |
| Priority    | —           |
| Next-subtask-id | 0005 |

## Goal

Run the doc pipeline end-to-end against a test source tree and validate the output
matches the two test cases defined in the brainstorm.

## Context

Test case 1 (zero documentation): run against a small source tree with no existing
.md files. Validate: every source file has a companion .md, every directory has a
README.md, cross-component docs appear at composite levels, no source files modified.

Test case 2 (partial documentation): run against a source tree with some existing
docs (the ai-builder orchestrator directory is a candidate). Validate: existing
correct docs preserved, gaps filled, stale docs updated, no duplication.

Target candidate for test case 1: the `fibonacci` regression test repo or a
purpose-built 3–4 package Go service under `sandbox/`.

Run with the doc machine: `--state-machine machines/doc/default.json`.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [x] [X-b9529c-0000-create-regression-test-dir](X-b9529c-0000-create-regression-test-dir/)
- [x] [X-b9529c-0001-copy-user-service-source-as-template](X-b9529c-0001-copy-user-service-source-as-template/)
- [x] [X-b9529c-0002-reset-copies-source-to-sandbox](X-b9529c-0002-reset-copies-source-to-sandbox/)
- [x] [X-b9529c-0003-setup-task-system-and-pipeline-task](X-b9529c-0003-setup-task-system-and-pipeline-task/)
- [x] [X-b9529c-0004-reset-run-and-gold-scripts](X-b9529c-0004-reset-run-and-gold-scripts/)
<!-- subtask-list-end -->

## Notes

_None._
