# Task: pipeline-theory-of-operation-doc

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status      | —                      |
| Epic        | main               |
| Tags        | —               |
| Parent      | 49352f-redesign-pipeline-communication-architecture             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Write a theory-of-operation document for the redesigned pipeline. The document
should cover:

- End-to-end flow from Oracle job submission to pipeline completion
- Role of each agent — ARCHITECT (decompose and design modes), IMPLEMENTOR,
  TESTER, DECOMPOSE_HANDLER, LEAF_COMPLETE_HANDLER, DOCUMENTER_POST_ARCHITECT,
  DOCUMENTER_POST_IMPLEMENTOR — with a concrete walkthrough of what each
  receives, does, and emits
- How the frame stack works and what `handoff_history` contains at each stage
- How `task.json` fields (`goal`, `context`, `complexity`, `output_dir`,
  `last-task`, `level`, `name`, `design`, `acceptance_criteria`,
  `test_command`, `documents_written`, `execution_log`, `run_summary`) are
  written and consumed across agents
- How the two-tree structure (task dir tree vs output dir tree) maps to
  each other and how `source_dir` in decompose output drives placement
- Agent output format: XML `<response>` block for ARCHITECT and IMPLEMENTOR;
  `OUTCOME:`/`HANDOFF:` plain lines for internal agents
- Post-completion flow: metrics write → README render → master-index rebuild →
  TOP_RENAME_PENDING deferred rename
- Run-dir separation (`--run-dir`): what sidecar files live there and why
- Loop detection: sliding window, what it guards against
- Resume protocol: `--resume`, `--clean-resume`, `handoff-state.json`

Place the document at `ai-builder/orchestrator/theory-of-operation.md`.

## Context

The pipeline was substantially redesigned across subtasks 0000–0031 of the
parent task. The major changes since the original design (0000–0018):

- **0019** — `render_readme.py`: README.md generated from task.json (not
  hand-written); TOP-level tasks get run summary + execution log
- **0020** — `build_master_index.py`: output dir `.md` files with
  Purpose:/Tags: headers are indexed into `master-index.md`
- **0021** — post-completion flow: after LEAF_COMPLETE_HANDLER signals
  HANDLER_ALL_DONE, orchestrator writes metrics, renders README, rebuilds
  master index, then applies the deferred rename
- **0022** — resume execution-log continuity: prior log entries are seeded
  into the new run on `--resume`
- **0023** — in-memory state passthrough: `task_state` dict eliminates
  disk round-trips; IMPLEMENTOR/TESTER read design fields from memory
- **0024** — pipeline loop detection: sliding window of (role, job_doc)
  pairs; halts with error if same pair recurs within 8 steps
- **0025** — verified Purpose:/Tags: doc headers; fixed component README.md
  indexing in `build_master_index.py`
- **0026** — write-before-rename fix: TOP_RENAME_PENDING protocol defers
  the build-N → X-build-N rename until after all post-run writes
- **0027** — run history archiving: `reset.sh` saves execution.log,
  task.json, README.md to `runs/YYYY-MM-DD-HH-MM-SS/` and appends to
  `run-history.md`
- **0028** — `--run-dir` flag: sidecar files (execution.log,
  current-job.txt, handoff-state.json, last-job.json) separated from
  generated code output
- **0029** — XML structured output: ARCHITECT and IMPLEMENTOR now emit
  `<response>` XML blocks instead of fenced JSON blocks; parser tries XML
  first, falls back to JSON
- **0030** — agent prompt audit: removed stale "edit job document in place"
  and "Suggested Tools" instructions; added `agent-roles.md`
- **0031** — documentation quality: mandatory source file headers
  (Purpose:/Tags: package-level comments); concrete companion `.md` doc
  requirements for IMPLEMENTOR; named detail files (api.md, models.md,
  etc.) for ARCHITECT

The theory-of-operation doc should describe the pipeline as it stands after
all of these changes — both for future human maintainers and to give incoming
AI sessions a complete mental model without needing to read every source file.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
