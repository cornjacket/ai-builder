# Agent Roles

Purpose: Canonical reference for every agent in the pipeline — what it receives,
what it produces, and what outcomes it can emit.
Tags: orchestrator, pipeline, architecture

This document covers all agents defined in `machines/builder/default.json`. AI agents
receive a text prompt built by the orchestrator; internal agents are Python
classes that run directly without invoking a model.

---

## Summary Table

| Agent | Type | Receives | Produces | Valid outcomes |
|-------|------|----------|----------|----------------|
| [ARCHITECT](#architect) | AI (claude/gemini) | Inline: goal, context, complexity, level, output dir; job doc path | Design: README.md in output dir, XML response with design/acceptance_criteria/test_command. Decompose: XML response with components array | `ARCHITECT_DESIGN_READY`, `ARCHITECT_DECOMPOSITION_READY`, `ARCHITECT_NEEDS_REVISION`, `ARCHITECT_NEED_HELP` |
| [IMPLEMENTOR](#implementor) | AI (claude/gemini) | Inline: goal, context, design, acceptance criteria, test command, output dir | Source files written to output dir; optional companion `.md`; XML response | `IMPLEMENTOR_IMPLEMENTATION_DONE`, `IMPLEMENTOR_NEEDS_ARCHITECT`, `IMPLEMENTOR_NEED_HELP` |
| [DECOMPOSE_HANDLER](#decompose_handler) | Internal | Components array (from ARCHITECT XML); job doc path | Pipeline subtask directories + task.jsons created; `current-job.txt` advanced | `HANDLER_SUBTASKS_READY`, `HANDLER_STOP_AFTER`, `HANDLER_NEED_HELP` |
| [LEAF_COMPLETE_HANDLER](#leaf_complete_handler) | Internal | `current-job.txt`; run dir | `on-task-complete.sh` run; directory renamed `X-`; `current-job.txt` advanced | `HANDLER_SUBTASKS_READY`, `HANDLER_ALL_DONE`, `HANDLER_STOP_AFTER`, `HANDLER_NEED_HELP` |
| [TESTER](#tester) | Internal | `test_command` from `task.json` | Subprocess exit code | `TESTER_TESTS_PASS`, `TESTER_TESTS_FAIL`, `TESTER_NEED_HELP` |
| [DOCUMENTER_POST_ARCHITECT](#documenter_post_architect--documenter_post_implementor) | Internal | Job doc path; output dir | `.md` files indexed into output dir README.md | `DOCUMENTER_DONE` |
| [DOCUMENTER_POST_IMPLEMENTOR](#documenter_post_architect--documenter_post_implementor) | Internal | Job doc path; output dir | `.md` files indexed into output dir README.md | `DOCUMENTER_DONE` |

---

## State Machine Flow

```
ARCHITECT ──design──► DOCUMENTER_POST_ARCHITECT ──► IMPLEMENTOR
    │                                                     │
    │                                           IMPLEMENTOR_IMPLEMENTATION_DONE
    │                                                     │
    │                                          DOCUMENTER_POST_IMPLEMENTOR
    │                                                     │
    └──decompose──► DECOMPOSE_HANDLER ──► ARCHITECT      TESTER
                                          (next comp)      │
                                                   TESTS_PASS
                                                           │
                                              LEAF_COMPLETE_HANDLER
                                               /           \
                                        SUBTASKS_READY   ALL_DONE
                                               │
                                           ARCHITECT
                                          (next sibling)
```

ARCHITECT_NEEDS_REVISION loops back to ARCHITECT. IMPLEMENTOR_NEEDS_ARCHITECT
loops back to ARCHITECT. TESTER_TESTS_FAIL loops back to IMPLEMENTOR. All
`_NEED_HELP` outcomes halt the pipeline.

---

## ARCHITECT

**Role file:** `roles/ARCHITECT.md`

The ARCHITECT designs the system. It never writes code, runs tests, or edits
the job document. It operates in one of two modes based on the `Complexity:`
field injected inline by the orchestrator.

### What it receives

The orchestrator injects inline into the prompt:

| Field | Source |
|-------|--------|
| `Goal` | `task.json → goal` |
| `Context` | `task.json → context` |
| `Complexity` | `task.json → complexity` |
| `Task Level` | `task.json → level` (`TOP` or `INTERNAL`) |
| Output directory path | `task.json → output_dir` |
| Job document path | `current-job.txt` (for supplementary reading only) |
| Handoff history | In-memory `handoff_history` list |

### Decompose Mode (`Complexity: —` or `composite`)

Identifies the top-level components of a service and returns them as a
structured array. The orchestrator's DECOMPOSE_HANDLER creates a pipeline
subtask and output subdirectory for each component.

**Produces:** XML `<response>` block with `outcome`, `handoff`, and
`<components>` array. Each `<component>` has `name`, `complexity`,
`source_dir`, and `description`.

The `description` field is critical — DECOMPOSE_HANDLER copies it verbatim
into each component's `goal` field in `task.json`. The design-mode ARCHITECT
for that component will only see this description as its goal.

### Design Mode (`Complexity: atomic`)

Produces a full design for a single atomic component. Writes `README.md` to
the output directory (mandatory for all non-`integrate` components), then
emits design fields in the XML response.

**Produces:**
- `README.md` in the output directory (with Purpose/Tags header, file index, overview)
- XML `<response>` block with `outcome`, `handoff`, `documents_written`,
  `design`, `acceptance_criteria`, `test_command`

The orchestrator stores `design`, `acceptance_criteria`, `test_command`, and
`documents_written` in `task.json` and in-memory `task_state` so downstream
agents (IMPLEMENTOR, TESTER) can access them without reading the job document.

**Special case — `integrate` component:** Wires sibling components together
(e.g. writes `main.go`). Does not write a README.md; sets `documents_written:
false`. Writes to the parent output directory directly (same directory as the
sibling packages).

---

## IMPLEMENTOR

**Role file:** `roles/IMPLEMENTOR.md`

The IMPLEMENTOR writes code. It does not design, and it does not run
acceptance tests.

### What it receives

The orchestrator injects inline into the prompt (all from `task_state` /
`task.json`, set when ARCHITECT returned `ARCHITECT_DESIGN_READY`):

| Field | Source |
|-------|--------|
| `Goal` | `task.json → goal` |
| `Context` | `task.json → context` |
| `Design` | `task.json → design` (set by ARCHITECT) |
| `Acceptance Criteria` | `task.json → acceptance_criteria` (set by ARCHITECT) |
| `Test Command` | `task.json → test_command` (set by ARCHITECT) |
| Output directory path | `task.json → output_dir` |
| Handoff history | In-memory `handoff_history` list |

### What it produces

- Source files written to the output directory
- Optional companion `.md` file for non-obvious implementation details
- XML `<response>` block with `outcome`, `handoff`, `documents_written`

The IMPLEMENTOR always runs a syntax/compile check after writing each file.
It does not run acceptance tests — that is TESTER's responsibility.

---

## DECOMPOSE_HANDLER

**Type:** Internal (Python function `_run_decompose_internal`)

Receives the components array parsed from ARCHITECT's XML response and creates
the pipeline subtask tree.

### What it does

For each component:
1. Runs `new-pipeline-subtask.sh` to create a task directory under the current
   job's parent
2. Writes `complexity`, `depth`, `goal` (= component description), `context`
   (ancestry chain), `output_dir`, and optionally `last-task` / `level` into
   the component's `task.json`
3. Creates the component's output subdirectory (keyed by `source_dir`); skips
   subdirectory creation for `integrate` (writes to parent dir directly)
4. Seeds `README.md` and `Context` sections in the component's task README

After all components are created, runs `set-current-job.sh` to point
`current-job.txt` at the first component's README, then transitions to
`ARCHITECT` to begin designing that component.

**Non-obvious:** `context` is a labelled ancestry chain (`### Level N —
<task-name>`) appended at each descent. This prevents the flat-copy
duplication that occurred when context was copied verbatim at every level.

---

## LEAF_COMPLETE_HANDLER

**Type:** Internal (Python function `_run_lch_internal`, driven by shell script
`on-task-complete.sh` / `advance-pipeline.sh`)

Runs after TESTER_TESTS_PASS to mark the completed task done and advance
`current-job.txt` to the next sibling or parent.

### What it does

1. Calls `on-task-complete.sh --current <job_doc> --output-dir <run_dir>`,
   which in turn calls `advance-pipeline.sh`
2. `advance-pipeline.sh` runs `complete-task.sh` on the finished component,
   renames its directory to `X-<name>`, and either points `current-job.txt`
   at the next sibling (`NEXT <path>`) or signals completion (`DONE`)

**TOP_RENAME_PENDING protocol:** When the pipeline is finishing the last
component (the one whose grandparent is a human-owned boundary), the rename of
the top-level build directory (`build-1 → X-build-1`) is deferred. LCH emits
`TOP_RENAME_PENDING <dir>` and the orchestrator captures it. After all
post-run writes (metrics, README render, master index), the orchestrator
applies the rename as the absolute last step. This ensures `task.json`
paths remain valid while metrics are being written.

---

## TESTER

**Type:** Internal (Python function `_run_tester_internal`)

Runs the test command and returns pass or fail. This is a simple subprocess
wrapper — no AI reasoning is involved.

### What it does

1. Reads `test_command` from `task.json` in the current job's directory
2. Runs it as a shell subprocess
3. Returns `TESTER_TESTS_PASS` (exit 0) or `TESTER_TESTS_FAIL` (non-zero)
   with full stdout/stderr in the handoff

If `test_command` is absent or `task.json` cannot be read, returns
`TESTER_NEED_HELP`.

---

## DOCUMENTER_POST_ARCHITECT / DOCUMENTER_POST_IMPLEMENTOR

**Type:** Internal (Python function `_run_documenter_internal`)

Scans the output directory for `.md` files and rebuilds the output `README.md`
with a documentation index. Runs as a mandatory post-step after ARCHITECT
(design mode) and after IMPLEMENTOR.

### What it does

1. Reads `documents_written` from `task.json`. If `false` or absent, returns
   `DOCUMENTER_DONE` immediately (no-op).
2. Walks the output directory for `*.md` files (excluding the root `README.md`
   itself and `master-index.md`)
3. Extracts `Purpose:` (first sentence) and `Tags:` from each file's header
4. Rebuilds the output directory's `README.md` with a design-docs index
   (ARCHITECT-written files) and an implementation-docs index
   (IMPLEMENTOR-written files)

**Note:** `DOCUMENTER_POST_ARCHITECT` and `DOCUMENTER_POST_IMPLEMENTOR` are
the same internal function invoked at different pipeline positions. The
distinction exists in the state machine to allow future divergence (e.g.
different doc validation logic post-ARCHITECT vs post-IMPLEMENTOR).
