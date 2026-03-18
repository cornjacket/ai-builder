# Task: add-status-and-reviews-to-target

| Field    | Value                |
|----------|----------------------|
| Status   | draft           |
| Epic     | main             |
| Tags     | tooling, target, project-management             |
| Parent   | —           |
| Priority | MED         |
| Next-subtask-id | 0000               |
## Description

Extend `target/setup-project.sh` to include `project/status/` and
`project/reviews/` in the installed skeleton, and add corresponding
instructions to the target's `CLAUDE.md` so that AI agents working in the
target repo know how to use them.

**Changes required:**

- `target/setup-project.sh` — add `project/status/` and `project/reviews/`
  to the directories created during installation (with `.gitkeep` files)
- `target/project/README.md` — create (mirroring `project/README.md` in
  ai-builder) to document the purpose of tasks/, status/, and reviews/ at
  the appropriate abstraction level for a target repo
- `target/init-claude-md.sh` — add a `project/status/` section to the
  task management block injected into the target's CLAUDE.md, including:
  - Purpose of status/ as session continuity for AI agents
  - Sign-off convention (user says "sign off", AI writes status summary)
  - Instruction to read the most recent status file at session start
- `target/verify-setup.sh` — add checks for `project/status/` and
  `project/reviews/` directories

**Note:** `project/reviews/` directory structure and artifact format depend
on `9b9d18-design-reviews-directory` being resolved first. The directory
can be created in the skeleton now; the format documentation should wait.

## Documentation

- Update `target/SETUP.md` to mention status/ and reviews/ in the installed
  structure
- The sign-off convention and status/ instructions belong in the target
  CLAUDE.md block injected by `init-claude-md.sh`

## Subtasks

<!-- When a subtask is finished, run complete-subtask.sh to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

Depends on `9b9d18-design-reviews-directory` for the full reviews/ format,
but the directory skeleton and status/ instructions can be done independently.

Related: `3230ef-design-workspace-claude-md-boundary` — the sign-off and
session continuity instructions also need to account for the CWD/spawning
model once that is resolved.
