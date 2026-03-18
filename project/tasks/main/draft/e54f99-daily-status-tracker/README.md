# Task: daily-status-tracker

| Field    | Value                                    |
|----------|------------------------------------------|
| Status   | draft                                    |
| Epic     | main                                     |
| Tags     | tooling, orchestrator, project-management |
| Parent   | —                                        |
| Priority | MED                                      |
| Next-subtask-id | 0000               |
## Description

A user-invocable function (slash command or CLI flag) that allows the AI to
proactively review what work was completed during the current session or day,
generate a concise status summary, and save it to a persistent file for later
reference.

**What it does:**
- Queries the task system (`list-tasks.sh --all`) to identify tasks and
  subtasks that moved to `complete` today (based on file modification time
  or a date stamp in the task README)
- Summarises work in progress (tasks currently in `in-progress/`)
- Highlights what is next (top of `backlog/` by priority)
- Saves the status report to `project/status/YYYY-MM-DD.md` for historical
  reference
- Optionally appends to a running `project/status/CHANGELOG.md`

**Invocation:**
- As a user function in Claude Code: `/status` or similar
- As a standalone script: `project/tasks/scripts/daily-status.sh`
- The AI can also invoke it proactively at the end of a session

**Status report format:**
```
# Status — YYYY-MM-DD

## Completed Today
- [task-name] — brief description

## In Progress
- [task-name] — brief description

## Up Next (from backlog)
- [task-name] [PRIORITY]

## Notes
(free-form observations about blockers, decisions made, etc.)
```

**Design questions to resolve:**
- How do we detect "completed today" reliably? Options: file mtime,
  a `completed_at` field in the task README, or the AI inferring from
  session context
- Should the AI generate the Notes section, or is it always human-written?
- Should status files be committed automatically or left unstaged for
  human review?

**Status: DRAFT — requires review before implementation begins.**

## Documentation

Once implemented, document in `CLAUDE.md` as a workflow tool available
to both human and AI users.

## Subtasks

<!-- When a subtask is finished, run complete-subtask.sh to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

The status history in `project/status/` becomes a lightweight project log —
useful for onboarding new contributors, generating release notes, and giving
an AI agent context about recent history when starting a new session.
