# Task: document-flexible-task-system-usage

| Field       | Value                              |
|-------------|------------------------------------|
| Status      | draft                              |
| Epic        | main                               |
| Tags        | documentation, task-management     |
| Parent      | —                                  |
| Priority    | HIGH                               |
| Complexity  | —                                  |
| Stop-after  | false                              |
| Last-task   | false                              |

## Goal

Document the task management system as a general-purpose filesystem convention
that can organise any kind of project work — not just engineering tasks — and
provide concrete examples of how to use it with custom-named directory trees
in `target/`.

## Context

The task management system is a filesystem convention backed by bash scripts.
The scripts work on any directory tree that follows the convention — they are
not coupled to `project/tasks/`. This means the same scripts can manage
engineering tasks, build history, design reviews, release checklists, incident
logs, research decisions, and more — each in its own named directory with its
own template.

This insight emerged during design discussions around composite decomposition
and the separation of human task artifacts from pipeline job documents. Full
context in:

- `sandbox/brainstorm-composite-decomposition-gap.md`
  (section: "⚠️ IMPORTANT: The filesystem is the implementation")

## Description

Produce documentation that:

1. **Explains the core abstraction**: a directory is a thing, a README
   describes it, subtasks are its parts, status folders track its lifecycle.
   The scripts are tools that operate on any tree following this shape.

2. **Documents how to create a custom-named tree** in a target repo:
   - How to set up a new root (e.g. `project/reviews/`, `project/projects/`,
     `project/decisions/`)
   - Whether `setup-project.sh` needs to be extended, or whether a lightweight
     `init-tree.sh` is more appropriate
   - How to provide a custom `task-template.md` per root

3. **Provides concrete usage examples** (see brainstorm for full list):
   - Multi-service build history (`projects/service-1/build-1/`, `build-2/`)
   - Design review process (`reviews/`)
   - Architectural decision log (`decisions/`)
   - Release management (`releases/`)
   - Incident tracking (`incidents/`)
   - Content pipeline, onboarding, etc.

4. **Documents the `target/projects/` convention**: the recommended layout
   for long-running build projects in a target repo, where each service has
   a directory and each pipeline run is a named subdirectory.

## Documentation

Deliverable is a new file: `target/USAGE-EXAMPLES.md` (or similar) plus
updates to `target/project/tasks/README.md` to note the system's generality.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
