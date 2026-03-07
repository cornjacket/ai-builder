# Lesson 036 — Use Directory Structure as Status Indicator

**Category:** architecture
**Source project:** Cornjacket Platform
**Date:** 2026-02-13

## Context

Task tracking systems often store status as metadata inside files (e.g., `**Status:** In Progress` in a YAML header). To know a task's status, you must open and read the file. This is invisible from the file system and requires parsing — both for humans browsing and AI agents triaging work.

## Lesson

Use directory location to convey state. Instead of a flat task directory with status fields, organize tasks into status-based subdirectories (`inbox/`, `backlog/`, `in-progress/`, `completed/`, `wont-do/`). Moving a file between directories is the status transition — `git mv tasks/backlog/task.md tasks/in-progress/task.md` changes status and is naturally tracked in commit history. This is the Kanban board principle applied to the file system: physical position conveys state.

Benefits for AI agents:
- `ls tasks/in-progress/` instantly shows active work without parsing files
- Status transitions are git operations, giving full audit trail
- No risk of status metadata falling out of sync with reality

## Decision Guidance

When designing a task tracking system for AI-assisted projects, prefer directory-as-status over metadata-as-status. The overhead of `git mv` is trivial compared to the clarity gained. Reserve metadata inside files for properties that don't map to a linear workflow (priority, assignee, epic membership).

## Related Lessons

- [003](003-every-change-needs-a-task-document.md) — task docs are the unit that moves between directories
- [035](035-organize-documents-for-ai-readability.md) — directory structure as an organizational tool for AI
