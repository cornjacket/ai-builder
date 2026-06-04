# Project

This directory contains all persistent project management artifacts for
ai-builder. It is the authoritative record of what is being built, what has
been decided, and what happened — across both human and AI sessions.

---

## Structure

```
project/
    tasks/      # task management system — what needs to be done
    status/     # periodic status reports — narrative synthesis of what shipped
    reviews/    # formal review artifacts — what was decided and why
    scripts/    # cross-cutting process scripts
```

---

## tasks/

The task management system. All work is tracked here before it begins.
Tasks are organized by epic and status (inbox, draft, backlog, in-progress,
complete, wont-do). Managed via scripts in `tasks/scripts/`.

**Full documentation:** [`tasks/README.md`](tasks/README.md)

### Subtask ordering convention

Subtask directory names follow the pattern `{parent-id}-{NNNN}-{name}`.
The `NNNN` four-digit number **defines the intended implementation order**.
Subtasks must be worked in ascending numeric order unless the parent README
explicitly states otherwise.

If the intended order changes, use `tasks/scripts/reorder-subtasks.py` to
renumber directories to match. The numbers are the contract — never implement
out of sequence without first reordering.

### Completion convention

When a subtask is completed, its directory is renamed with an `X-` prefix:
`X-{parent-id}-{NNNN}-{name}`. The number is preserved for audit purposes.
Completed subtasks appear as `[x]` in the parent README's subtask list.
The `X-` prefix makes completion status visible at a glance in any file
viewer, without opening any file.

---

## status/

Periodic status reports. Each report is a **delta document** covering the
period since the previous report — narrative synthesis, not a daily log.
Cadence is operator-driven (weekly, twice-weekly, daily) and is not tied
to session boundaries. Files are named `YYYY-MM-DD.md`, where the date is
the as-of date of the report.

Each status report records:
- **Work Completed** — narrative summary of what shipped during the
  period (not a 1:1 restatement of the git commit history, which is the
  atomic per-task ground truth)
- **Work In Progress** — what is currently open
- **Next Up** — what comes after the in-progress work
- **Key Decisions** — non-obvious decisions worth carrying forward

**Purpose for AI agents:** `status/` is how a new session picks up where
the last one left off. Before starting work, read the most recent status
report to understand current state. New reports are produced when the
operator says **"write a status report"** (see below).

When writing a status report, also add a new row to the top of the log
table in `project/status/README.md` with the date and a one-line summary.

**Worktrees:** status reports are produced from `main/` only — they are
a coordination artifact, not per-worktree state.

---

## scripts/

Cross-cutting process scripts that operate on repo-level artifacts and don't
belong to a single subsystem.

Distinct from `tasks/scripts/`, which manages `tasks/` artifacts only.

---

## reviews/

Formal review artifacts produced after human review sessions. Stores
decisions, findings, and follow-up actions from code and architecture reviews.

Consulted by:
- The ARCHITECT during planning (to avoid repeating past mistakes)
- The Oracle during human review (to accumulate review history)
- The TM during re-planning (to understand what went wrong)

**Status:** directory structure and artifact format are not yet fully designed.
See `project/tasks/main/draft/37a660-design-oracle-and-pipeline-phases/9b9d18-design-reviews-directory/`
for the design task.

---

## Writing a status report

When the operator says **"write a status report"** (or natural variants:
"status report", "draft a status report", "write status", "write up the
period"), the AI will:

1. Identify the period since the most recent status report.
2. Synthesise what shipped during that period (drawing on the git commit
   history, completed tasks, and any in-flight work) — not a line-by-line
   replay of `git log`, but a narrative summary of themes and outcomes.
3. Note what is in progress, what is next, and any key decisions made
   during the period.
4. Write the report to `project/status/YYYY-MM-DD.md`, where the date is
   the as-of date.
5. Add a new row to the top of the log table in
   `project/status/README.md`.
6. Commit if requested.

Status reports are produced on operator request, not at session end.
Cadence is flexible — weekly, twice-weekly, or daily, as the operator
chooses. This mirrors a real staff status meeting.
