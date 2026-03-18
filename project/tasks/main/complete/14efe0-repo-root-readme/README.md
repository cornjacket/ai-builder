# Task: repo-root-readme

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Priority    | MED           |
| Next-subtask-id | 0000               |

## Goal

Write a `README.md` at the repository root that describes the entire ai-builder
system and how to use it. This is the entry point for anyone new to the repo —
human or AI — and should give a complete picture without requiring them to read
every subdirectory first.

Sections to include:

1. **What ai-builder is** — a multi-role AI pipeline that takes a job document
   from specification to tested implementation using specialist agents
   (ARCHITECT, IMPLEMENTOR, TESTER).

2. **Repository layout** — top-level directory map with one-line descriptions:
   `ai-builder/`, `roles/`, `target/`, `tests/`, `sandbox/`, `project/`.

3. **How the pipeline works** — brief end-to-end summary: job document →
   orchestrator → agents → tested implementation. Reference
   `ai-builder/orchestrator/README.md` for full detail.

4. **Two modes** — non-TM mode (`--job`) and TM mode (`--target-repo`); when
   to use each.

5. **Quick start: non-TM mode** — minimal example running the orchestrator
   against a hand-written job document.

6. **Quick start: TM mode** — the three steps (create build task, fill in
   Goal/Context, run orchestrator) using `new-pipeline-build.sh` and
   `set-current-job.sh`. Reference `ai-builder/orchestrator/README.md` for
   the full command.

7. **Roles** — one-line summary of each role (ARCHITECT, IMPLEMENTOR, TESTER,
   DECOMPOSE_HANDLER, LEAF_COMPLETE_HANDLER) with a pointer to `roles/`.

8. **Task management** — brief explanation of the task system in `project/`;
   pointer to `project/tasks/README.md`.

9. **Regression tests** — where they live (`tests/regression/`), how to reset
   and run one.

10. **Key design docs** — a short list of the most important companion
    documents: `ai-builder/orchestrator/README.md`, `pipeline-behavior.md`,
    `decomposition.md`, `monitoring.md`.

## Context

The repo currently has no root-level README. Anyone landing on the repo root —
including AI agents reading it at the start of a session — has no orientation
document. All the detail is present in subdirectory READMEs and companion docs
but there is no single entry point that ties it together.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
