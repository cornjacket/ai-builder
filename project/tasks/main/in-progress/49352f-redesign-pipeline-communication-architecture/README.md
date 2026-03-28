# Task: redesign-pipeline-communication-architecture

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | in-progress             |
| Epic        | main               |
| Tags        | orchestrator, architecture, pipeline               |
| Priority    | HIGH           |
| Next-subtask-id | 0033 |

## Goal

Redesign the pipeline's communication architecture so that agents communicate
through a single structured channel (prose + terminal JSON block) rather than
the current mix of disk file writes, regex-parsed response text, and JSON.

## Context

The pipeline evolved incrementally from a human task management system, causing
pipeline tasks to inherit Markdown as their format even though machines need
structured data. The result is three incoherent communication channels in use
simultaneously:

- ARCHITECT writes a `## Components` Markdown table to README.md on disk;
  DECOMPOSE_HANDLER parses it back with regex
- Outcomes and handoffs travel through response text parsed with regex
- Completion state lives in `task.json` as JSON

The proposed direction: agents emit prose followed by a fenced JSON block
containing all machine-readable output (outcome, handoff, components, design,
documents). The orchestrator parses the JSON block; prose streams in real time
for observability. Pipeline task state moves to pure JSON; README.md for
pipeline tasks becomes a generated view, not the authoritative record.

## Notes

Brainstorm: `sandbox/brainstorm-pipeline-communication-architecture.md`

**Implementation order** (subtask IDs reflect creation order, not dependency order):

```
0000 → 0001 → 0002 → 0003+0004* → 0005 → 0006 → 0007 → 0008 → 0009 → 0010 → 0011 → 0012 → 0013 → 0014 → 0015 → 0016 → 0017 → 0018
```

`*` 0003 and 0004 must be implemented and deployed atomically — deploying
0003 alone breaks DECOMPOSE_HANDLER.

0005 (handoff frame stack redesign) requires 0004 (`output_dir` in
`task.json`) and must precede 0008 (handoff persist/inject), which
serializes the new frame structure.

0009 (resume stale frame detection) requires 0008 (handoff persist/inject,
which provides the load path) and 0005 (which defines the component frame
type being detected).

0010 (port-regression-task-json) must be done before running regression tests.

0018 (post-completion flow) requires 0015 + 0016 + 0017.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [x] [X-49352f-0000-oracle-goal-context-in-task-json](X-49352f-0000-oracle-goal-context-in-task-json/)
- [x] [X-49352f-0001-orchestrator-job-param-replace-current-job-txt](X-49352f-0001-orchestrator-job-param-replace-current-job-txt/)
- [x] [X-49352f-0002-leaf-complete-handler-last-job-json](X-49352f-0002-leaf-complete-handler-last-job-json/)
- [x] [X-49352f-0003-architect-decompose-returns-components-json](X-49352f-0003-architect-decompose-returns-components-json/)
- [x] [X-49352f-0004-decompose-handler-dual-tree-and-output-dir](X-49352f-0004-decompose-handler-dual-tree-and-output-dir/)
- [x] [X-49352f-0005-handoff-frame-stack-redesign](X-49352f-0005-handoff-frame-stack-redesign/)
- [x] [X-49352f-0006-architect-atomic-returns-design-json](X-49352f-0006-architect-atomic-returns-design-json/)
- [x] [X-49352f-0007-integrate-step-parent-output-dir](X-49352f-0007-integrate-step-parent-output-dir/)
- [x] [X-49352f-0008-handoff-state-persist-and-inject](X-49352f-0008-handoff-state-persist-and-inject/)
- [x] [X-49352f-0009-resume-stale-frame-detection](X-49352f-0009-resume-stale-frame-detection/)
- [x] [X-49352f-0010-port-regression-task-json](X-49352f-0010-port-regression-task-json/)
- [x] [X-49352f-0011-pipeline-component-tests](X-49352f-0011-pipeline-component-tests/)
- [x] [X-49352f-0012-run-regression-bootstrap-component-tests](X-49352f-0012-run-regression-bootstrap-component-tests/)
- [x] [X-49352f-0013-documenter-scan-and-index](X-49352f-0013-documenter-scan-and-index/)
- [x] [X-49352f-0014-architect-doc-format-convention](X-49352f-0014-architect-doc-format-convention/)
- [x] [X-49352f-0015-implementor-inline-content-companion-md](X-49352f-0015-implementor-inline-content-companion-md/)
- [x] [X-49352f-0016-tester-internal-handler](X-49352f-0016-tester-internal-handler/)
- [x] [X-49352f-0017-post-run-metrics-in-task-json](X-49352f-0017-post-run-metrics-in-task-json/)
- [x] [X-49352f-0018-architect-source-dir-in-decompose-json](X-49352f-0018-architect-source-dir-in-decompose-json/)
- [x] [X-49352f-0019-readme-render-script](X-49352f-0019-readme-render-script/)
- [x] [X-49352f-0020-master-index-rebuild-script](X-49352f-0020-master-index-rebuild-script/)
- [x] [X-49352f-0021-post-completion-flow](X-49352f-0021-post-completion-flow/)
- [x] [X-49352f-0022-resume-execution-log-continuity](X-49352f-0022-resume-execution-log-continuity/)
- [x] [X-49352f-0023-orchestrator-in-memory-state-passthrough](X-49352f-0023-orchestrator-in-memory-state-passthrough/)
- [x] [X-49352f-0024-pipeline-loop-detection](X-49352f-0024-pipeline-loop-detection/)
- [x] [X-49352f-0025-verify-output-doc-headers](X-49352f-0025-verify-output-doc-headers/)
- [x] [X-49352f-0026-final-invocation-not-recorded](X-49352f-0026-final-invocation-not-recorded/)
- [x] [X-49352f-0027-preserve-run-history](X-49352f-0027-preserve-run-history/)
- [x] [X-49352f-0028-per-run-output-directory](X-49352f-0028-per-run-output-directory/)
- [x] [X-49352f-0029-xml-structured-output-format](X-49352f-0029-xml-structured-output-format/)
- [x] [X-49352f-0030-audit-agent-prompts-for-stale-instructions](X-49352f-0030-audit-agent-prompts-for-stale-instructions/)
- [x] [X-49352f-0031-investigate-output-documentation-quality](X-49352f-0031-investigate-output-documentation-quality/)
- [ ] [49352f-0032-pipeline-theory-of-operation-doc](49352f-0032-pipeline-theory-of-operation-doc/)
<!-- subtask-list-end -->

## Notes

_None._
