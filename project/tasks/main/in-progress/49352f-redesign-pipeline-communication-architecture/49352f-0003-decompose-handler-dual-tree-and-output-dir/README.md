# Task: decompose-handler-dual-tree-and-output-dir

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

Update DECOMPOSE_HANDLER to read components from the ARCHITECT JSON response
(not README.md), create both the task directory tree and the output directory
tree simultaneously for each component, and store `output_dir` in each
component's `task.json`.

**Must be deployed atomically with subtask 0002** — deploying 0002 alone breaks
DECOMPOSE_HANDLER since it would still try to read the old Markdown table.

## Context

Currently DECOMPOSE_HANDLER: (1) reads the `## Components` table from README.md
using regex; (2) creates task directories via `new-pipeline-subtask.sh`; (3)
relies on IMPLEMENTOR to implicitly create output subdirectories when it writes
source files. This is incoherent — directory structure should be a deliberate
upfront decision.

**Changes required:**

1. **Read from JSON response** — DECOMPOSE_HANDLER receives the parsed
   `components` array from the orchestrator (extracted from ARCHITECT's JSON
   block). No file read, no regex.

2. **Dual tree creation** — for each component (excluding `integrate`):
   - Create task directory: `project/tasks/.../handlers/task.json`
   - Create output directory: `user-service-output/handlers/`
   Both in a single operation. Two trees stay in sync by construction.

3. **`output_dir` in `task.json`** — each component's `task.json` carries the
   absolute path to its output directory. The orchestrator reads `output_dir`
   from `task.json` when building prompts for ARCHITECT and IMPLEMENTOR.

4. **`integrate` excluded from output dir creation** — `integrate`'s
   `output_dir` is set to the parent's output directory (see subtask 0009).

5. **Placeholder README** — write a placeholder `README.md` into each new
   output directory at scaffold time (ARCHITECT fills it in via docs;
   DOCUMENTER renders the final index).

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
