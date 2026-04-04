# Task: design-workspace-claude-md-boundary

| Field    | Value                |
|----------|----------------------|
| Status   | draft           |
| Epic     | main             |
| Tags     | tooling, claude-md, workspace             |
| Parent   | —           |
| Priority | MED         |
| Category    | workspace-mgmt         |
| Next-subtask-id | 0000               |
## Description

When a target repository is set up inside a parent workspace directory that
contains multiple git worktrees or repos (e.g. `workspace/repo-1/`,
`workspace/repo-2/`), Claude's upward CLAUDE.md traversal will cross repo
boundaries unless explicitly stopped.

Placing a `CLAUDE.md` directly in the parent workspace directory serves two
purposes:

1. **Boundary** — stops Claude from traversing further up the directory tree
2. **Shared context** — can carry workspace-level instructions that all child
   repos should inherit (or be a minimal stub if no shared context is needed)

This task covers:
- Deciding whether `setup-project.sh` or `init-claude-md.sh` should handle
  creating the workspace-level boundary `CLAUDE.md`
- Defining what content (if any) belongs in a workspace-level `CLAUDE.md`
  vs repo-level `CLAUDE.md`
- Documenting the recommended workspace layout and how the boundary works
- Updating `SETUP.md` and `target/verify-setup.sh` if the boundary file
  becomes part of the expected installation

## Documentation

Update `target/SETUP.md` to describe the workspace boundary pattern.
Consider whether `verify-setup.sh` should optionally check for a parent
boundary file.

## Subtasks

<!-- When a subtask is finished, run complete-subtask.sh to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

**Planning vs. design distinction:**
Deciding *what* the CLAUDE.md hierarchy looks like is a design step (done
once, upfront). Deciding *where* to place a CLAUDE.md for a specific new
directory is a planning step — it belongs in the TM/ARCHITECT phase of each
job, not in a one-time setup script.

This means:
- `setup-project.sh` and `init-claude-md.sh` handle the static skeleton only
- For each job that introduces a new directory, the ARCHITECT must decide
  whether that directory warrants its own CLAUDE.md and create it as an
  explicit task in the plan
- The review process should include a CLAUDE.md placement checkpoint:
  the reviewer should confirm the ARCHITECT's hierarchy decisions before
  implementation begins in new directories
- `verify-setup.sh` can only check the static skeleton — runtime CLAUDE.md
  placements are job-specific and not verifiable upfront

**ARCHITECT ownership:**
The ARCHITECT is responsible for deciding which directories represent a
distinct enough abstraction layer to warrant their own CLAUDE.md. This
judgment happens during the Planning phase and is part of the review artifact.

**Bootstrapping problem:**
The first time the TM plans work in a new directory, no CLAUDE.md exists
there yet. The ARCHITECT must create it before the IMPLEMENTOR starts work,
meaning CLAUDE.md creation is always an early task in any plan that
introduces new directories.

**Workspace layout this addresses:**
```
workspace/
    CLAUDE.md          ← boundary + optional shared config
    repo-1/
        CLAUDE.md      ← repo-specific config
        project/tasks/
    repo-2/
        CLAUDE.md
        project/tasks/
```

A minimal boundary stub contains only a comment explaining its purpose and
no instructions, so child repos fully control their own context. A legitimate
workspace-level config would carry instructions common to all repos (e.g.
shared coding standards, team conventions).
