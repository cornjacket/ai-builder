# Task: fix-purpose-tags-markdown-rendering

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 69f226-pipeline-doc-generation-bugs             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Fix the markdown rendering defect where `Purpose:` and `Tags:` appear on the same
line in the markdown viewer. Each field should render as a separate visual line.

## Context

Agent-authored `.md` files use the format:

```
Purpose: One sentence description.
Tags: architecture, design
```

In the markdown viewer these two lines collapse onto one line because there is no
blank line between them. CommonMark requires a blank line (or two trailing spaces)
to produce a line break between non-list block elements. Fix the `doc-format.md`
standard and update any role prompts that specify the format so agents emit a blank
line between `Purpose:` and `Tags:`.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
