# Project

This directory contains all persistent project management artifacts for
ai-builder. It is the authoritative record of what is being built, what has
been decided, and what happened — across both human and AI sessions.

---

## Structure

```
project/
    tasks/      # task management system — what needs to be done
    status/     # session and daily status logs — what was done
    reviews/    # formal review artifacts — what was decided and why
```

---

## tasks/

The task management system. All work is tracked here before it begins.
Tasks are organized by epic and status (inbox, draft, backlog, in-progress,
complete, wont-do). Managed via scripts in `tasks/scripts/`.

**Full documentation:** [`tasks/README.md`](tasks/README.md)

---

## status/

Session and daily status logs. One file per day, named `YYYY-MM-DD.md`.

Each status file records:
- What was completed
- What was worked on but not completed
- What is in progress or coming up next
- Any key decisions made

**Purpose for AI agents:** `status/` is how a new session picks up where the
last one left off. Before starting work, read the most recent status file to
understand current state. At the end of a session, write a status file
summarising what was done (see Sign-off below).

**Convention:** files are named `YYYY-MM-DD.md`. If multiple sessions occur
on the same day, append to the existing file rather than creating a new one.

---

## reviews/

Formal review artifacts produced after human review sessions. Stores
decisions, findings, and follow-up actions from code and architecture reviews.

Consulted by:
- The ARCHITECT during planning (to avoid repeating past mistakes)
- The Oracle during human review (to accumulate review history)
- The PM during re-planning (to understand what went wrong)

**Status:** directory structure and artifact format are not yet fully designed.
See `project/tasks/main/draft/37a660-design-oracle-and-pipeline-phases/9b9d18-design-reviews-directory/`
for the design task.

---

## Sign-off

When ending a session, the user should say **"sign off"** to trigger a status
summary. The AI will:

1. Summarise all work done during the session
2. Note what is in progress, what is next, and any open decisions
3. Write the summary to `project/status/YYYY-MM-DD.md`
4. Commit if requested

This ensures the next session — whether the same day or weeks later — has a
clear starting point.
