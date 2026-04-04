# Task: parallel-pipeline-via-git-worktrees

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | draft             |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Category    | orchestrator-core      |
| Next-subtask-id | 0000               |

## Goal

Enable the orchestrator to run multiple pipeline instances in parallel, each
isolated in its own git worktree of the target repository. This supports two
use cases:

1. **Parallel features** — implement N independent features simultaneously,
   each in its own branch, without the pipelines interfering with each other.

2. **Parallel variants** — implement the same feature N times with different
   approaches (different machines, different model configs, different prompts)
   and compare the results before deciding which branch to keep or merge.

## Context

### The problem today

The orchestrator writes directly into the target repo (`--target-repo`). Two
concurrent runs on the same repo corrupt each other — they share the task tree,
the same branch, and the same output directory. The sandbox enforcement rule
exists precisely because of this: only one regression run at a time.

### How git worktrees help

`git worktree add` creates a second (or Nth) working directory linked to the
same `.git` object store but checked out on a separate branch. Each worktree
has its own working tree, its own `HEAD`, and its own index. The pipeline can
run independently in each worktree as if it had its own repo clone — without
the overhead of a full clone.

### What needs to be built

**Option A: Worktree manager (launcher layer)**

A new script or command (`run-parallel.sh` or `orchestrator parallel`) that:
1. Accepts a list of jobs (or a single job + a count N for variant mode)
2. Creates N git worktrees from the target repo, each on a fresh branch
3. Launches N orchestrator instances concurrently, one per worktree
4. Streams per-instance logs
5. Reports when all instances complete (pass/fail per branch)
6. (Variant mode) Optionally opens a diff or summary for human review

This is purely a launch/lifecycle layer. The orchestrator itself is unchanged.

**Option B: New machine type (orchestrator layer)**

A `parallel` machine that the orchestrator itself knows how to interpret. The
machine JSON defines N sub-pipelines. The orchestrator fans out, waits for all
to complete, and then optionally runs a comparison/merge stage.

This is more invasive — the orchestrator loop would need to support parallel
execution paths — but it integrates cleanly with the existing machine abstraction.

### Key open questions

- **Which option?** Option A is simpler and composable; Option B is more
  integrated. Brainstorm before committing.
- **Branch naming** — how should worktree branches be named? `feature/X-1`,
  `feature/X-2`, or caller-supplied?
- **Output directory isolation** — each orchestrator instance needs its own
  `--output-dir`. Does this live under `sandbox/` with a run ID, or alongside
  the worktree?
- **Task tree isolation** — the task system lives in the ai-builder repo, not
  the target. Multiple runs can share the task tree safely. But the pipeline
  subtask READMEs must be per-run, which the current `--output-dir` already
  handles.
- **Comparison stage** — for variant mode, what does comparison look like?
  A diff of generated files? Token cost comparison? A new `COMPARATOR` role
  that reads N output dirs and produces a recommendation?
- **Merge strategy** — after picking a winner in variant mode, how does the
  winning branch get integrated? Squash merge? Interactive rebase? Human step?

### Relationship to machine abstraction

The `46f78a` restructuring established `machines/builder/` as the seam for
defining alternative pipelines. A `machines/parallel/` machine (if Option B)
would live there alongside `machines/builder/`. Its format would need to
express sub-pipeline definitions — likely as a list of machine references or
inline role configs.

If Option A, no new machine is needed — the parallel launcher wraps the
existing machines unchanged.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
