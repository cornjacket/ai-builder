# Task: redesign-pipeline-communication-architecture

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | in-progress             |
| Epic        | main               |
| Tags        | orchestrator, architecture, pipeline               |
| Priority    | HIGH           |
| Next-subtask-id | 0018 |

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
0000 → 0001 → 0002 → 0003+0004* → 0005 → 0006 → 0007 → 0008 → 0017 → 0009 → 0010 → 0011 → 0012 → 0013 → 0014 → 0015 → 0016
```

`*` 0003 and 0004 must be implemented and deployed atomically — deploying
0003 alone breaks DECOMPOSE_HANDLER.

0005 (handoff frame stack redesign) requires 0004 (`output_dir` in
`task.json`) and must precede 0008 (handoff persist/inject), which
serializes the new frame structure.

0017 (resume stale frame detection) requires 0008 (handoff persist/inject,
which provides the load path) and 0005 (which defines the component frame
type being detected).

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [ ] [49352f-0000-oracle-goal-context-in-task-json](49352f-0000-oracle-goal-context-in-task-json/)
- [ ] [49352f-0001-orchestrator-job-param-replace-current-job-txt](49352f-0001-orchestrator-job-param-replace-current-job-txt/)
- [ ] [49352f-0002-leaf-complete-handler-last-job-json](49352f-0002-leaf-complete-handler-last-job-json/)
- [ ] [49352f-0003-architect-decompose-returns-components-json](49352f-0003-architect-decompose-returns-components-json/)
- [ ] [49352f-0004-decompose-handler-dual-tree-and-output-dir](49352f-0004-decompose-handler-dual-tree-and-output-dir/)
- [ ] [49352f-0005-handoff-frame-stack-redesign](49352f-0005-handoff-frame-stack-redesign/)
- [ ] [49352f-0006-architect-atomic-returns-design-json](49352f-0006-architect-atomic-returns-design-json/)
- [ ] [49352f-0007-integrate-step-parent-output-dir](49352f-0007-integrate-step-parent-output-dir/)
- [ ] [49352f-0008-handoff-state-persist-and-inject](49352f-0008-handoff-state-persist-and-inject/)
- [ ] [49352f-0009-resume-stale-frame-detection](49352f-0009-resume-stale-frame-detection/)
- [ ] [49352f-0010-pipeline-component-tests](49352f-0010-pipeline-component-tests/)
- [ ] [49352f-0011-documenter-scan-and-index](49352f-0011-documenter-scan-and-index/)
- [ ] [49352f-0012-implementor-inline-content-companion-md](49352f-0012-implementor-inline-content-companion-md/)
- [ ] [49352f-0013-tester-internal-handler](49352f-0013-tester-internal-handler/)
- [ ] [49352f-0014-post-run-metrics-in-task-json](49352f-0014-post-run-metrics-in-task-json/)
- [ ] [49352f-0015-readme-render-script](49352f-0015-readme-render-script/)
- [ ] [49352f-0016-master-index-rebuild-script](49352f-0016-master-index-rebuild-script/)
- [ ] [49352f-0017-post-completion-flow](49352f-0017-post-completion-flow/)
<!-- subtask-list-end -->

## Notes

_None._
