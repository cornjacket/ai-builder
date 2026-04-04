# Task: investigate-task-partitioning-for-parallel-worktrees

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status | in-progress |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Created     | 2026-04-03            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

Analyse the codebase and backlog to identify refactoring classes — groups of
tasks that touch disjoint sets of source files — so that multiple worktrees
can run in parallel with minimal merge conflicts.

## Context

We have a growing backlog of high-priority tasks. Running them sequentially
on main is safe but slow. Git worktrees enable parallel development, but only
if the tasks in different worktrees don't compete for the same files. A merge
becomes painful when two branches both modify `orchestrator.py` or the same
role prompt.

The goal is to partition the backlog into classes where each class has low
overlap with the others. Each class maps to one worktree that can be developed,
tested, and merged independently.

**What this task should produce:**

1. **File ownership map** — for each significant source file or directory,
   which backlog tasks are likely to touch it. Built by reading task Goals and
   cross-referencing the codebase structure.

2. **Partition proposal** — a set of refactoring classes (e.g. "orchestrator
   core", "role prompts", "task scripts", "regression infrastructure") where
   tasks within a class share files and tasks across classes do not. Each class
   can become a worktree branch.

3. **Conflict hotspots** — files that multiple classes need to touch (e.g.
   `orchestrator.py` is touched by almost everything). Flag these explicitly
   so they can be sequenced rather than parallelised.

4. **Recommended merge order** — for classes that do share files, suggest the
   order that minimises rebase friction.

**Approach:**
- Read all backlog and in-progress task Goals/Context
- Map each to the files/directories it will likely modify (based on the task
  description and current codebase layout)
- Cluster by file overlap
- Produce the partition as a document in `sandbox/` for discussion before
  acting on it

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

Output document: [`sandbox/task-partition-analysis.md`](../../../../../sandbox/task-partition-analysis.md)

8 partition classes identified. Primary conflict hotspot is `orchestrator.py` (touched by Classes 1, 2, 3).
Safe parallel worktrees right now: Class 3 (acceptance-spec), Class 5 (regression infra), Class 6 (task scripts), Class 7 (docs).
Recommended merge order: Class 1 → 3 → 5/6/7 (parallel) → 4 → 2 → 8.
